import sys
from pathlib import Path
import time
import random

# Add workspace root to python path to support absolute imports when running as a standalone script
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import os

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

from backend.vector_db.retriever import (
    search,
    search_compliance,
    search_hr,
    build_context,
    KNOWLEDGE_BASES
)
from backend.services.intent_classifier import IntentClassifier


# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ==========================================================
# GEMINI LLM (Using API Key for fast responses)
# ==========================================================

gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=GEMINI_API_KEY
)

gemini_fallback_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=GEMINI_API_KEY
)

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
            is_temporary = any(code in err_msg for code in ["503", "500", "429", "UNAVAILABLE", "ResourceExhausted", "high demand", "overloaded"])
            
            if is_temporary and attempt < max_retries - 1:
                # Exponential backoff with jitter
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"[WARNING] Temporary LLM error encountered: {err_msg}. Retrying in {sleep_time:.2f}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                raise e


# ==========================================================
# AGENT
# ==========================================================

compliance_agent = Agent(
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

    llm=gemini_llm
)


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
    # 1. INTENT CLASSIFICATION
    intent = IntentClassifier.classify(query)
    
    collection_name = "GENERAL_LLM"
    results = []
    
    # 2. RETRIEVE FROM CORRESPONDING KNOWLEDGE BASE
    if intent == "COMPLIANCE":
        collection_name = KNOWLEDGE_BASES["COMPLIANCE"]
        try:
            results = search_compliance(query, top_k=10)
        except Exception as e:
            print(f"Error querying latam_compliance: {e}")
            results = []
            
    elif intent == "HR":
        collection_name = KNOWLEDGE_BASES["HR"]
        try:
            results = search_hr(query, top_k=10)
        except Exception as e:
            print(f"Error querying hr_playbook: {e}")
            results = []

    # 3. TASK LOGGING (Required format)
    print(f"[INFO] Intent: {intent}")
    print(f"[INFO] Collection: {collection_name}")
    print(f"[INFO] Retrieved Chunks: {len(results)}")

    # 4. FALLBACK LOGIC
    fallback_triggered = False
    if intent == "GENERAL" or not results:
        fallback_triggered = True

    if fallback_triggered:
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
        
        # Fast direct LLM invocation with retry and fallback
        def call_direct():
            return gemini_llm.call(prompt)
            
        try:
            answer = execute_with_retry_and_fallback(call_direct)
        except Exception as e:
            print(f"[WARNING] General LLM call failed with primary model: {e}. Trying fallback model gemini-1.5-flash...")
            def call_direct_fallback():
                return gemini_fallback_llm.call(prompt)
            try:
                answer = execute_with_retry_and_fallback(call_direct_fallback)
            except Exception as final_err:
                print(f"[ERROR] General LLM fallback call also failed: {final_err}")
                raise final_err
        
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
        agent=compliance_agent
    )

    # Reset agent LLM to primary just in case it was changed to fallback in a previous execution
    compliance_agent.llm = gemini_llm

    # 8. CREW EXECUTION
    crew = Crew(
        agents=[compliance_agent],
        tasks=[compliance_task],
        process=Process.sequential,
        verbose=True
    )

    def kickoff_crew():
        return crew.kickoff()

    try:
        result = execute_with_retry_and_fallback(kickoff_crew)
    except Exception as e:
        print(f"[WARNING] Crew execution failed with primary model: {e}. Trying fallback model gemini-1.5-flash...")
        try:
            compliance_agent.llm = gemini_fallback_llm
            # Recreate task and crew to ensure settings are correctly propagated
            fallback_task = Task(
                description=description,
                expected_output=expected_output,
                agent=compliance_agent
            )
            fallback_crew = Crew(
                agents=[compliance_agent],
                tasks=[fallback_task],
                process=Process.sequential,
                verbose=True
            )
            def kickoff_fallback_crew():
                return fallback_crew.kickoff()
            result = execute_with_retry_and_fallback(kickoff_fallback_crew)
        except Exception as fallback_err:
            print(f"[ERROR] Fallback model Crew execution failed: {fallback_err}. Falling back to direct LLM call...")
            try:
                result = execute_with_retry_and_fallback(lambda: gemini_fallback_llm.call(description))
            except Exception as final_err:
                print(f"[ERROR] All models and approaches failed: {final_err}")
                raise final_err
    
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
