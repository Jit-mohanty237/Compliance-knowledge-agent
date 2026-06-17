# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from services.compliance import process_compliance_chat
from compliance_agent import get_gemini_llm
import time

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    """
    Accepts a user question, queries ChromaDB, runs the CrewAI compliance
    agent, and returns the response alongside the session_id.
    """
    try:
        res_dict, session_id = process_compliance_chat(
            query=payload.message,
            session_id=payload.session_id
        )
        return ChatResponse(
            response=res_dict.get("answer"),
            session_id=session_id,
            intent=res_dict.get("intent"),
            source_collection=res_dict.get("source_collection"),
            documents_used=res_dict.get("documents_used")
        )
    except Exception as e:
        # Wrap underlying exceptions in a clear HTTP 500 error
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating compliance guidance: {str(e)}"
        )


@router.post("/test-gemini")
def test_gemini_endpoint(payload: ChatRequest):
    """
    Directly invokes the Gemini LLM to test API latency.
    """
    try:
        t0 = time.time()
        llm = get_gemini_llm()
        response = llm.call(payload.message)
        latency = time.time() - t0
        print(f"[TIME] Direct Gemini call took {latency:.4f}s")
        return {"response": str(response)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in direct Gemini call: {str(e)}"
        )
