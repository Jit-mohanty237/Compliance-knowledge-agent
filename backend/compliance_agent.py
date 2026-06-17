from services.intent_classifier import IntentClassifier
from vector_db.retriever import (
    search,
    search_compliance,
    search_hr,
    build_context,
    KNOWLEDGE_BASES
)
from crewai.llm import LLM
from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
import time
import random

# Add workspace root to python path to support absolute imports when running as a standalone script
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# pyrefly: ignore [missing-import]


# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ==========================================================
# GEMINI LLM (Using API Key for fast responses)
# ==========================================================

# ==========================================================
# LAZY LOAD LLM & AGENT WITH CACHING & TIMEOUTS
# ==========================================================

_gemini_llm = None
_gemini_fallback_llm = None
_compliance_agent = None

BYPASS_CREWAI_DEBUG = False

def get_gemini_llm():
    global _gemini_llm
    if _gemini_llm is None:
        print("[DEBUG] Initializing gemini_llm (should happen once only)")
        _gemini_llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=GEMINI_API_KEY,
            timeout=60
        )
    return _gemini_llm

def get_gemini_fallback_llm():
    global _gemini_fallback_llm
    if _gemini_fallback_llm is None:
        print("[DEBUG] Initializing gemini_fallback_llm (should happen once only)")
        _gemini_fallback_llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=GEMINI_API_KEY,
            timeout=60
        )
    return _gemini_fallback_llm

def get_compliance_agent():
    global _compliance_agent
    if _compliance_agent is None:
        print("[DEBUG] Initializing compliance_agent (should happen once only)")
        _compliance_agent = Agent(
            role="Senior LATAM Compliance Officer",
            goal="""
            Provide accurate LATAM compliance guidance using
            retrieved compliance records.

            Use only the provided compliance context.

            Do not invent laws, articles, penalties,
            or compliance requirements.
            """,
            backstory="""
            You are a Senior LATAM Compliance Officer.

            You specialize in:
            - Labor Laws,
            - Employment Contracts,
            - Working Hours & Overtime,
            - Payroll & Social Security,
            - Taxation,
            - Leave & Benefits,
            - Hiring Compliance,
            - Contractor Classification,
            - Termination & Severance,
            - Documentation Required,
            - Compliance Risks,
            - Collective Bargaining,
            - Union Regulations,
            - Remote Work Compliance,
            - Data Privacy Compliance,
            - Health & Safety Compliance,
            - Immigration & Work Permit Compliance,
            - Anti-Discrimination Laws,
            - Mandatory Employee Benefits,
            - Payroll Reporting,
            - Employee Registration Requirements
            across LATAM countries.

            You answer questions using retrieved
            compliance information.
            """,
            verbose=True,
            allow_delegation=False,
            llm=get_gemini_llm()
        )
    return _compliance_agent

def init_agents():
    """
    Eagerly pre-load and initialize LLMs and Agents on startup.
    This should be called at startup to prevent latency on first query.
    """
    print("[DEBUG] Eagerly pre-initializing CrewAI LLMs and Agents on startup...")
    t_start = time.time()
    get_gemini_llm()
    get_gemini_fallback_llm()
    get_compliance_agent()
    print(f"[DEBUG] CrewAI LLMs and Agents pre-initialized in {time.time() - t_start:.4f}s")


def is_rate_limit_error(e: Exception) -> bool:
    err_msg = str(e)
    return any(code in err_msg for code in ["429", "ResourceExhausted", "Quota exceeded"])


def execute_with_retry_and_fallback(fn, max_retries=3):
    """
    Executes a model function (crew.kickoff or llm.call) with retries 
    on temporary API errors (like 503 UNAVAILABLE or 429 Rate Limit).
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            err_msg = str(e)
            
            # If it is a rate limit error, raise immediately to avoid hanging the thread
            if is_rate_limit_error(e):
                print(f"[DEBUG] Rate limit (429) detected. Raising immediately without retry.")
                raise e

            is_temporary = any(code in err_msg for code in [
                               "503", "500", "UNAVAILABLE", "high demand", "overloaded"])

            if is_temporary and attempt < max_retries - 1:
                # Exponential backoff with jitter
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(
                    f"[WARNING] Temporary LLM error encountered: {err_msg}. Retrying in {sleep_time:.2f}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                raise e


# ==========================================================
# QUERY EXECUTION FUNCTION (FOR SERVICES & API)
# ==========================================================

def run_compliance_query(query: str, chat_history: list = None) -> dict:
    """
    Execute a query using Multi-KB RAG.

    Why this exists:
        Routes queries based on intent (COMPLIANCE, HR, or GENERAL) to 
        prevent search pollution. Integrates fallback LLM generation 
        for general small talk or missing vector database records.

    How it works:
        1. Runs IntentClassifier on query.
        2. Retrieves from either latam_compliance or hr_playbook.
        3. If no documents match, or intent is GENERAL, falls back to direct Gemini LLM.
        4. Otherwise, runs the CrewAI Agent context-matching task.
        5. Returns structured dictionary containing response + metadata.
        """
    request_start = time.time()

    # Log that Chroma initialization is done at startup (zero request overhead)
    print("[TIME] Chroma Initialization: Done at startup (0.0000s request overhead)")

    # 1. INTENT CLASSIFICATION
    t0 = time.time()
    intent = IntentClassifier.classify(query)
    t_intent = time.time() - t0
    print(f"[TIME] Intent Classification: {intent} ({t_intent:.4f}s)")

    collection_name = "GENERAL_LLM"
    results = []

    # 2. RETRIEVE FROM CORRESPONDING KNOWLEDGE BASE
    t_retrieve_start = time.time()
    if intent == "COMPLIANCE":
        collection_name = KNOWLEDGE_BASES["COMPLIANCE"]
        try:
            results = search_compliance(query, top_k=10)
        except Exception as e:
            print(f"[DEBUG] Collection selection failure / Query error for compliance: {e}")
            results = []

    elif intent == "HR":
        collection_name = KNOWLEDGE_BASES["HR"]
        try:
            results = search_hr(query, top_k=10)
        except Exception as e:
            print(f"[DEBUG] Collection selection failure / Query error for HR: {e}")
            results = []
    
    t_retrieved = time.time() - t_retrieve_start
    print(f"[TIME] Chroma Query: {t_retrieved:.4f}s")
    print(f"[TIME] Collection Selection: {collection_name}")
    print(f"[TIME] Retrieval Completed: {len(results)} chunks ({t_retrieved:.4f}s)")

    # 3. TASK LOGGING (Required format & Detailed debug logging)
    print(f"[DEBUG] Incoming Query: {query}")
    print(f"[DEBUG] Classified Intent: {intent}")
    print(f"[DEBUG] Selected Collection: {collection_name}")
    print(f"[DEBUG] Chunk Count: {len(results)}")
    if results:
        print(f"[DEBUG] First Chunk Metadata: {results[0].get('metadata')}")

    print(f"[INFO] Intent: {intent}")
    print(f"[INFO] Collection: {collection_name}")
    print(f"[INFO] Retrieved Chunks: {len(results)}")

    # 4. FALLBACK LOGIC AUDIT & EXPLICIT LOGGING
    fallback_triggered = False
    fallback_reason = ""
    
    if intent == "GENERAL":
        fallback_triggered = True
        fallback_reason = "Intent classification failure (fell back to GENERAL)"
        print(f"[DEBUG] Intent classification failure: fallback to GENERAL")
    elif not results:
        fallback_triggered = True
        fallback_reason = "Chroma retrieval returning zero results"
        print(f"[DEBUG] Chroma retrieval returning zero results for collection: {collection_name}")
    
    if fallback_triggered:
        print(f"[DEBUG] LLM fallback activation (Reason: {fallback_reason})")
        # Build direct LLM prompt (incorporating memory if available)
        prompt = ""
        if chat_history:
            prompt += "CONVERSATION HISTORY:\n"
            for msg in chat_history:
                role = msg.get("role", "user").upper()
                content = msg.get("content", "")
                prompt += f"- {role}: {content}\n"
            prompt += "====================================================\n\n"

        prompt += f"USER QUESTION: {query}\n\n"
        prompt += (
            "Instructions:\n"
            "You are a professional assistant. Provide a helpful, clear, and accurate response "
            "to the user's question. If they are greeting you or doing small talk, respond warmly and professionally."
        )

        t_gemini_start = time.time()
        # Fast direct LLM invocation with retry and fallback
        def call_direct():
            return get_gemini_llm().call(prompt)

        try:
            answer = execute_with_retry_and_fallback(call_direct)
        except Exception as e:
            if is_rate_limit_error(e):
                print(f"[DEBUG] General LLM rate-limited. Failing fast.")
                return {
                    "answer": "The assistant is currently experiencing high demand (rate limit exceeded). Please wait a few seconds and try again.",
                    "intent": intent,
                    "source_collection": "GENERAL_LLM",
                    "documents_used": []
                }
            print(
                f"[WARNING] General LLM call failed with primary model: {e}. Trying fallback model gemini-1.5-flash...")

            def call_direct_fallback():
                return get_gemini_fallback_llm().call(prompt)
            try:
                answer = execute_with_retry_and_fallback(call_direct_fallback)
            except Exception as final_err:
                if is_rate_limit_error(final_err):
                    print(f"[DEBUG] Fallback General LLM rate-limited. Failing fast.")
                    return {
                        "answer": "The assistant is currently experiencing high demand (rate limit exceeded). Please wait a few seconds and try again.",
                        "intent": intent,
                        "source_collection": "GENERAL_LLM",
                        "documents_used": []
                    }
                print(
                    f"[ERROR] General LLM fallback call also failed: {final_err}")
                raise final_err

        t_gemini = time.time() - t_gemini_start
        print(f"[TIME] Gemini Execution: {t_gemini:.4f}s")
        t_total = time.time() - request_start
        print(f"[TIME] Total Request Time: {t_total:.4f}s")

        return {
            "answer": str(answer),
            "intent": intent,
            "source_collection": "GENERAL_LLM",
            "documents_used": []
        }

    # 5. CONTEXT PREPARATION
    context = build_context(results)

    # Extract unique source files used
    documents_used = list(set(
        item["metadata"].get("source_file", "latam_laws_flat.json")
        for item in results
        if item.get("metadata")
    ))

    # 5b. BYPASS CREWAI DEBUG MODE
    if BYPASS_CREWAI_DEBUG:
        t_total = time.time() - request_start
        print(f"[TIME] Total Request Time (Bypassed CrewAI): {t_total:.4f}s")
        retrieved_content = "\n\n".join([
            f"--- Chunk #{i+1} (Source: {r['metadata'].get('source_file', 'unknown') if r.get('metadata') else 'unknown'}) ---\n{r['document']}"
            for i, r in enumerate(results)
        ])
        return {
            "answer": f"[DEBUG] BYPASS_CREWAI_DEBUG is active. Retrieved {len(results)} chunks from {collection_name}.\n\n{retrieved_content}",
            "intent": intent,
            "source_collection": collection_name,
            "documents_used": documents_used
        }

    # 6. FORMAT CHAT HISTORY FOR CONTEXT
    history_context = ""
    if chat_history:
        history_context = "CONVERSATION HISTORY:\n"
        for msg in chat_history:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            history_context += f"- {role}: {content}\n"
        history_context += "====================================================\n\n"

    # 7. CHOOSE PROMPT BASED ON INTENT
    if intent == "COMPLIANCE":
        description = f"""
You are given retrieved compliance records and the current conversation history.

Use ONLY the information below.

If the answer is not found in the context, say:
'I could not find this information in the compliance database.'

====================================================

{history_context}RETRIEVED COMPLIANCE CONTEXT

{context}

====================================================

USER QUESTION

{query}

====================================================

Instructions:

1. Answer using the retrieved context.
2. Mention applicable laws.
3. Mention article numbers.
4. Mention compliance risks.
5. Mention penalties.
6. Mention practical HR guidance.
7. If information is missing,
   explicitly say so.
"""
        expected_output = """
A professional compliance response including:

- Applicable laws
- Article numbers
- Legal definitions
- Compliance risks
- Penalties
- HR considerations
- Practical recommendations
"""
    else:  # HR Intent
        description = f"""
You are given retrieved HR records and the current conversation history.

Use ONLY the information below.

If the answer is not found in the context, say:
'I could not find this information in the HR database.'

====================================================

{history_context}RETRIEVED HR CONTEXT

{context}

====================================================

USER QUESTION

{query}

====================================================

Instructions:

1. Answer using the retrieved context.
2. Detail relevant HR projects, timelines, action plans, business impacts, or success measures if present.
3. Provide practical, professional HR recommendations.
4. If information is missing,
   explicitly say so.
"""
        expected_output = """
A professional HR response including:

- Summary of HR programs and policies
- Associated frequencies and timelines
- Practical action plans or next steps
- Business impacts and success measures
"""

    compliance_task = Task(
        description=description,
        expected_output=expected_output,
        agent=get_compliance_agent()
    )

    # Reset agent LLM to primary just in case it was changed to fallback in a previous execution
    get_compliance_agent().llm = get_gemini_llm()

    # 8. CREW EXECUTION
    crew = Crew(
        agents=[get_compliance_agent()],
        tasks=[compliance_task],
        process=Process.sequential,
        verbose=True
    )

    def kickoff_crew():
        return crew.kickoff()

    t_crew_start = time.time()
    try:
        result = execute_with_retry_and_fallback(kickoff_crew)
    except Exception as e:
        if is_rate_limit_error(e):
            print(f"[DEBUG] Primary Crew execution rate-limited. Failing fast.")
            return {
                "answer": "The compliance assistant is currently experiencing high demand (rate limit exceeded). Please wait a few seconds and try again.",
                "intent": intent,
                "source_collection": collection_name,
                "documents_used": documents_used
            }
        print(
            f"[WARNING] Crew execution failed with primary model: {e}. Trying fallback model gemini-1.5-flash...")
        try:
            get_compliance_agent().llm = get_gemini_fallback_llm()
            # Recreate task and crew to ensure settings are correctly propagated
            fallback_task = Task(
                description=description,
                expected_output=expected_output,
                agent=get_compliance_agent()
            )
            fallback_crew = Crew(
                agents=[get_compliance_agent()],
                tasks=[fallback_task],
                process=Process.sequential,
                verbose=True
            )

            def kickoff_fallback_crew():
                return fallback_crew.kickoff()
            result = execute_with_retry_and_fallback(kickoff_fallback_crew)
        except Exception as fallback_err:
            if is_rate_limit_error(fallback_err):
                print(f"[DEBUG] Fallback Crew execution rate-limited. Failing fast.")
                return {
                    "answer": "The compliance assistant is currently experiencing high demand (rate limit exceeded). Please wait a few seconds and try again.",
                    "intent": intent,
                    "source_collection": collection_name,
                    "documents_used": documents_used
                }
            print(
                f"[ERROR] Fallback model Crew execution failed: {fallback_err}. Falling back to direct LLM call...")
            try:
                result = execute_with_retry_and_fallback(
                    lambda: get_gemini_fallback_llm().call(description))
            except Exception as final_err:
                if is_rate_limit_error(final_err):
                    print(f"[DEBUG] Final direct LLM execution rate-limited. Failing fast.")
                    return {
                        "answer": "The compliance assistant is currently experiencing high demand (rate limit exceeded). Please wait a few seconds and try again.",
                        "intent": intent,
                        "source_collection": collection_name,
                        "documents_used": documents_used
                    }
                print(f"[ERROR] All models and approaches failed: {final_err}")
                raise final_err
    t_crew = time.time() - t_crew_start
    print(f"[TIME] CrewAI Execution: {t_crew:.4f}s")
    t_total = time.time() - request_start
    print(f"[TIME] Total Request Time: {t_total:.4f}s")

    return {
        "answer": str(result),
        "intent": intent,
        "source_collection": collection_name,
        "documents_used": documents_used
    }


# ==========================================================
# CLI RUNNER (BACKWARDS COMPATIBILITY)
# ==========================================================

if __name__ == "__main__":
    print("\nLATAM Compliance & HR Assistant (CLI)\n")
    query = input("Enter your question: ")
    print("\nProcessing your query...\n")
    res = run_compliance_query(query)
    print("\n" + "=" * 80)
    print("RESPONSE")
    print("=" * 80 + "\n")
    print(res["answer"])
    print("\n" + "=" * 80)
    print("METADATA")
    print("=" * 80)
    print(f"Intent: {res['intent']}")
    print(f"Collection: {res['source_collection']}")
    print(f"Documents: {res['documents_used']}\n")
