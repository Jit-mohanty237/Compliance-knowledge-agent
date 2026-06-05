import sys
from pathlib import Path

# Add backend root to path to ensure compliance_agent can be imported cleanly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.compliance_agent import run_compliance_query
from backend.services.memory import get_session_history, add_message_to_session, create_session

def process_compliance_chat(query: str, session_id: str = None) -> tuple[dict, str]:
    """
    Coordinates session lookup, invokes the compliance agent, and saves
    the conversation history.
    
    Returns:
        tuple[dict, str]: (response_dict, session_id)
    """
    # 1. Initialize session if none was provided
    if not session_id:
        session_id = create_session()
        
    # 2. Retrieve history for the current session
    chat_history = get_session_history(session_id)
    
    # 3. Call the compliance query runner (passing history context)
    res_dict = run_compliance_query(query, chat_history=chat_history)
    
    # 4. Append current transaction to session history (using raw answer content)
    add_message_to_session(session_id, role="user", content=query)
    add_message_to_session(session_id, role="assistant", content=res_dict["answer"])
    
    return res_dict, session_id

