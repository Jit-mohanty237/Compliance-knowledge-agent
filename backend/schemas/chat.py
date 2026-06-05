# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    """
    Represents a single message in the chat conversation history.
    """
    role: str = Field(..., description="The sender's role, typically 'user' or 'assistant'")
    content: str = Field(..., description="The content text of the message")

class ChatRequest(BaseModel):
    """
    Schema for incoming chat requests.
    """
    message: str = Field(..., description="The user's compliance question")
    session_id: Optional[str] = Field(None, description="Unique session ID to retrieve conversation history")

class ChatResponse(BaseModel):
    """
    Schema for outgoing chat responses.
    """
    response: str = Field(..., description="The generated response from the compliance agent")
    session_id: str = Field(..., description="The session ID associated with the conversation")
    intent: Optional[str] = Field(None, description="The detected query intent")
    source_collection: Optional[str] = Field(None, description="The source collection searched")
    documents_used: Optional[List[str]] = Field(None, description="List of document source file names used for generating context")

