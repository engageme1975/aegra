"""State definitions for the UK Housing Agent."""

from typing import Optional
from langgraph.graph import MessagesState


class InputState(MessagesState):
    """Input state for the UK Housing Agent.
    
    Extends MessagesState which provides:
    - messages: List[AnyMessage] with add_messages reducer
    """
    pass


class State(InputState):
    """Complete state structure for the UK Housing Agent.
    
    Extends InputState with additional fields for routing decisions.
    """
    
    issue_type: Optional[str] = None
    """Detected housing issue type: heating, damp, repairs, or general."""
    
    current_agent: Optional[str] = None
    """Currently active specialist agent."""
