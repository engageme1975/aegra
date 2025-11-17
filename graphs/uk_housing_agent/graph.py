"""Main graph definition for the UK Housing Agent."""

from typing import Literal, cast
from datetime import UTC, datetime

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from uk_housing_agent.context import Context
from uk_housing_agent.state import InputState, State
from uk_housing_agent.tools import TOOLS
from langchain_openai import ChatOpenAI


# ======================================================================
# LLM Initialization
# ======================================================================

def get_intent_llm(runtime: Runtime[Context]) -> ChatOpenAI:
    """Initialize the LLM for intent detection."""
    return ChatOpenAI(
        model_name=runtime.context.model,
        api_key=runtime.context.openai_api_key,
        base_url=runtime.context.openai_api_base,
        temperature=0,
    )


def get_agent_llm(runtime: Runtime[Context]) -> ChatOpenAI:
    """Initialize the LLM for agent responses."""
    return ChatOpenAI(
        model_name=runtime.context.model,
        api_key=runtime.context.openai_api_key,
        base_url=runtime.context.openai_api_base,
        temperature=runtime.context.temperature,
        max_tokens=runtime.context.max_tokens,
    )


# ======================================================================
# Graph Nodes
# ======================================================================

async def detect_intent(
    state: State, runtime: Runtime[Context]
):
    """Detect the housing issue type from the user message.
    
    Args:
        state: Current graph state
        runtime: Runtime context with configuration
        
    Returns:
        Updated state with detected issue type
    """
    intent_llm = get_intent_llm(runtime)
    
    # Handle both dict and State object
    messages = state.get("messages", []) if isinstance(state, dict) else state.messages
    
    prompt = """Classify the user message into EXACTLY ONE category:
- heating: boiler errors, radiator issues, temperature, heating problems
- damp: damp, mold, mould, condensation, moisture, wet issues
- repairs: broken taps/pipes, cracked windows, electrical faults, doors, brickwork, roofing, painting
- general: other housing issues

Answer with ONLY the category name in lowercase, nothing else."""
    
    response = await intent_llm.ainvoke([
        SystemMessage(content=prompt),
        *messages
    ])
    
    detected = response.content.strip().lower()
    valid_types = {"heating", "damp", "repairs", "general"}
    issue_type = detected if detected in valid_types else "general"
    
    return {"issue_type": issue_type}


# ======================================================================
# Specialist Agent Nodes (One for each issue type)
# ======================================================================

async def heating_agent(
    state: State, runtime: Runtime[Context]
):
    """Handle heating-related issues."""
    model = get_agent_llm(runtime).bind_tools(TOOLS)
    
    messages = state.get("messages", []) if isinstance(state, dict) else state.messages
    
    system_prompt = """You are a heating system expert. Help users with boiler errors, 
radiator issues, temperature problems, and heating maintenance. Provide practical, 
safety-conscious advice."""
    
    response = cast(
        AIMessage,
        await model.ainvoke([
            SystemMessage(content=system_prompt),
            *messages
        ])
    )
    return {"messages": [response]}


async def damp_agent(
    state: State, runtime: Runtime[Context]
):
    """Handle damp and moisture-related issues."""
    model = get_agent_llm(runtime).bind_tools(TOOLS)
    
    messages = state.get("messages", []) if isinstance(state, dict) else state.messages
    
    system_prompt = """You are a damp and moisture specialist. Help users with mold, 
condensation, moisture, and dampness problems. Provide practical solutions and prevention tips."""
    
    response = cast(
        AIMessage,
        await model.ainvoke([
            SystemMessage(content=system_prompt),
            *messages
        ])
    )
    return {"messages": [response]}


async def repairs_agent(
    state: State, runtime: Runtime[Context]
):
    """Handle repairs and maintenance issues."""
    model = get_agent_llm(runtime).bind_tools(TOOLS)
    
    messages = state.get("messages", []) if isinstance(state, dict) else state.messages
    
    system_prompt = """You are a repairs and maintenance expert. Help users with plumbing, 
electrical, structural issues, broken fixtures, and general home maintenance. 
Provide practical advice and safety warnings when needed."""
    
    response = cast(
        AIMessage,
        await model.ainvoke([
            SystemMessage(content=system_prompt),
            *messages
        ])
    )
    return {"messages": [response]}


async def general_agent(
    state: State, runtime: Runtime[Context]
):
    """Handle general housing queries."""
    model = get_agent_llm(runtime).bind_tools(TOOLS)
    
    messages = state.get("messages", []) if isinstance(state, dict) else state.messages
    
    system_prompt = """You are a general housing advisor. Help users with any housing-related 
questions that don't fit into heating, damp, or repairs categories. Provide practical advice 
and guidance."""
    
    response = cast(
        AIMessage,
        await model.ainvoke([
            SystemMessage(content=system_prompt),
            *messages
        ])
    )
    return {"messages": [response]}


# ======================================================================
# Build Graph
# ======================================================================

builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# Add nodes
builder.add_node("detect_intent", detect_intent)
builder.add_node("heating_agent", heating_agent)
builder.add_node("damp_agent", damp_agent)
builder.add_node("repairs_agent", repairs_agent)
builder.add_node("general_agent", general_agent)

# Set entry point
builder.add_edge("__start__", "detect_intent")

# Route from detect_intent to appropriate agent (3 edges + general fallback)
def route_to_agent(state: State) -> str:
    """Route to agent based on detected issue type."""
    issue_type = state.get("issue_type", "general") if isinstance(state, dict) else (state.issue_type or "general")
    
    routing = {
        "heating": "heating_agent",
        "damp": "damp_agent",
        "repairs": "repairs_agent",
        "general": "general_agent",
    }
    
    return routing.get(issue_type, "general_agent")


builder.add_conditional_edges("detect_intent", route_to_agent)

# All agents route to END
builder.add_edge("heating_agent", END)
builder.add_edge("damp_agent", END)
builder.add_edge("repairs_agent", END)
builder.add_edge("general_agent", END)

# Compile the graph
graph = builder.compile()

