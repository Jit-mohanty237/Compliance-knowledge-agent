import uuid
from typing import Dict, List

# In-memory dictionary acting as our session store: {session_id: [messages]}
# In a distributed production environment, this should be replaced with Redis or a relational DB.
_session_store: Dict[str, List[dict]] = {}

def get_session_history(session_id: str) -> List[dict]:
    """
    Retrieve message history for a given session ID.
    Returns an empty list if session_id is not found or empty.
    """
    if not session_id:
        return []
    return _session_store.get(session_id, [])

def add_message_to_session(session_id: str, role: str, content: str) -> None:
    """
    Append a message (either 'user' or 'assistant') to the session history.
    """
    if not session_id:
        return
    if session_id not in _session_store:
        _session_store[session_id] = []
    _session_store[session_id].append({"role": role, "content": content})

def create_session() -> str:
    """
    Generate a new unique session ID and initialize its history.
    """
    new_id = str(uuid.uuid4())
    _session_store[new_id] = []
    return new_id

def clear_session(session_id: str) -> None:
    """
    Reset history for a given session ID.
    """
    if session_id in _session_store:
        _session_store[session_id] = []
