# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.compliance import process_compliance_chat

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
