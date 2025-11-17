"""Tools for the UK Housing Agent."""

from langchain_core.tools import tool


@tool
def search_housing_knowledge(query: str) -> str:
    """Search the UK housing knowledge base for relevant information.
    
    Args:
        query: The search query about housing issues
        
    Returns:
        Knowledge search results from the knowledge base
    """
    return f"Knowledge base results for: {query}"


@tool
def get_boiler_info(boiler_brand: str) -> str:
    """Get information about a specific boiler brand.
    
    Args:
        boiler_brand: The brand of boiler (e.g., Baxi, Vaillant, Worcester)
        
    Returns:
        Boiler specifications and common issues
    """
    return f"Boiler information for {boiler_brand}"


@tool
def get_repair_guidance(issue_type: str) -> str:
    """Get repair guidance for specific housing issues.
    
    Args:
        issue_type: The type of repair issue (heating, damp, repairs, etc.)
        
    Returns:
        Repair guidance and safety information
    """
    return f"Repair guidance for {issue_type}"


@tool
def schedule_engineer(issue_type: str, urgency: str) -> str:
    """Schedule an engineer visit for the issue.
    
    Args:
        issue_type: Type of issue requiring engineer
        urgency: Urgency level (low, medium, high, emergency)
        
    Returns:
        Confirmation of engineer scheduling
    """
    return f"Engineer scheduled for {issue_type} (urgency: {urgency})"


@tool
def escalate_to_human(reason: str) -> str:
    """Escalate issue to human support.
    
    Args:
        reason: Reason for escalation
        
    Returns:
        Escalation confirmation
    """
    return f"Issue escalated – {reason}"


# Export all available tools
TOOLS = [
    search_housing_knowledge,
    get_boiler_info,
    get_repair_guidance,
    schedule_engineer,
    escalate_to_human,
]
