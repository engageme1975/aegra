"""OpenAI-compatible API endpoints for chat completions

This module provides OpenAI API compatibility for LangGraph agents,
allowing any OpenAI SDK or client to interact with the agents.

Endpoints:
- GET /v1/models - List available models (graphs)
- POST /v1/chat/completions - Create chat completion
- POST /v1/chat/completions (streaming) - Streaming chat completion
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..core.auth_deps import get_current_user
from ..models import User
from ..services.langgraph_service import get_langgraph_service

router = APIRouter()
logger = structlog.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================


class ChatMessage(BaseModel):
    """OpenAI-compatible chat message"""

    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request"""

    model: str = Field(..., description="Model/Graph ID to use")
    messages: list[ChatMessage] = Field(..., description="Chat messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=1)
    stream: bool = Field(default=False, description="Whether to stream responses")
    stream_options: dict[str, Any] | None = Field(default=None)
    thread_id: str | None = Field(
        default=None, description="Thread ID for conversation continuity"
    )
    user: str | None = Field(default=None, description="User identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "agent",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the weather?"},
                ],
                "temperature": 0.7,
                "stream": False,
                "thread_id": "thread-123",
            }
        }


class ChatCompletionChoice(BaseModel):
    """OpenAI-compatible completion choice"""

    index: int = Field(default=0)
    message: ChatMessage = Field(...)
    finish_reason: str = Field(default="stop")
    logprobs: Any | None = Field(default=None)


class ChatCompletionUsage(BaseModel):
    """OpenAI-compatible usage statistics"""

    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response"""

    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid4()}")
    object: str = Field(default="chat.completion")
    created: int = Field(default_factory=lambda: int(datetime.now(UTC).timestamp()))
    model: str = Field(...)
    choices: list[ChatCompletionChoice] = Field(...)
    usage: ChatCompletionUsage = Field(default_factory=ChatCompletionUsage)
    system_fingerprint: str | None = Field(default=None)


class ChatCompletionStreamChoice(BaseModel):
    """OpenAI-compatible streaming choice"""

    index: int = Field(default=0)
    delta: ChatMessage = Field(...)
    finish_reason: str | None = Field(default=None)


class ChatCompletionStreamResponse(BaseModel):
    """OpenAI-compatible streaming response chunk"""

    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid4()}")
    object: str = Field(default="chat.completion.chunk")
    created: int = Field(default_factory=lambda: int(datetime.now(UTC).timestamp()))
    model: str = Field(...)
    choices: list[ChatCompletionStreamChoice] = Field(...)
    system_fingerprint: str | None = Field(default=None)


class ModelObject(BaseModel):
    """OpenAI-compatible model object"""

    id: str = Field(...)
    object: str = Field(default="model")
    created: int = Field(default_factory=lambda: int(datetime.now(UTC).timestamp()))
    owned_by: str = Field(default="aegra")
    permission: list[Any] = Field(default_factory=list)
    root: str | None = Field(default=None)
    parent: str | None = Field(default=None)


class ModelsResponse(BaseModel):
    """OpenAI-compatible models list response"""

    object: str = Field(default="list")
    data: list[ModelObject] = Field(...)


# ============================================================================
# Helper Functions
# ============================================================================


def _convert_messages_to_langgraph_format(messages: list[ChatMessage]) -> list[dict]:
    """Convert OpenAI messages to LangGraph format"""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    converted = []
    for msg in messages:
        if msg.role == "system":
            converted.append(SystemMessage(content=msg.content))
        elif msg.role == "user":
            converted.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            converted.append(AIMessage(content=msg.content))
    return converted


async def _get_graph_or_404(graph_id: str):
    """Get a graph by ID or raise 404"""
    langgraph_service = get_langgraph_service()
    try:
        graph = await langgraph_service.get_graph(graph_id)
        return graph
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Graph/Model '{graph_id}' not found"
        )


# ============================================================================
# API Endpoints
# ============================================================================


@router.get(
    "/v1/models",
    response_model=ModelsResponse,
    tags=["OpenAI Compatibility"],
    summary="List available models",
    description="Returns list of available LangGraph agents as models",
)
async def list_models(user: User = Depends(get_current_user)):
    """List all available models (graphs)"""
    langgraph_service = get_langgraph_service()
    graphs = langgraph_service.list_graphs()

    models = [
        ModelObject(
            id=graph_id,
            object="model",
            created=int(datetime.now(UTC).timestamp()),
            owned_by="aegra",
        )
        for graph_id in graphs
    ]

    return ModelsResponse(object="list", data=models)


@router.get(
    "/v1/models/{model_id}",
    response_model=ModelObject,
    tags=["OpenAI Compatibility"],
    summary="Get model details",
)
async def get_model(
    model_id: str, user: User = Depends(get_current_user)
):
    """Get details for a specific model"""
    await _get_graph_or_404(model_id)

    return ModelObject(
        id=model_id,
        object="model",
        created=int(datetime.now(UTC).timestamp()),
        owned_by="aegra",
    )


@router.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse | None,
    tags=["OpenAI Compatibility"],
    summary="Create chat completion",
    description="OpenAI-compatible chat completion endpoint. Set stream=true for streaming responses.",
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    user: User = Depends(get_current_user),
):
    """Create a chat completion (OpenAI-compatible)

    Supports both regular and streaming responses.
    """
    # Validate model exists
    graph = await _get_graph_or_404(request.model)

    # Use provided thread_id or generate new one
    thread_id = request.thread_id or f"thread-{uuid4()}"

    if request.stream:
        # Return streaming response
        return StreamingResponse(
            _stream_chat_completion(request, graph, thread_id, user),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # Return regular response
        return await _chat_completion_non_streaming(
            request, graph, thread_id, user
        )


async def _chat_completion_non_streaming(
    request: ChatCompletionRequest, graph: Any, thread_id: str, user: User
) -> ChatCompletionResponse:
    """Handle non-streaming chat completion"""
    try:
        # Convert messages to LangGraph format
        converted_messages = _convert_messages_to_langgraph_format(request.messages)

        # Build input state
        input_state = {
            "messages": converted_messages,
        }

        # Prepare config with thread for memory
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user.identity,
            }
        }

        # Invoke the graph
        result = await graph.ainvoke(input_state, config=config)

        # Extract response from result
        messages = result.get("messages", [])
        if not messages:
            response_content = "No response generated"
        else:
            # Get last message
            last_msg = messages[-1]
            response_content = (
                last_msg.content
                if hasattr(last_msg, "content")
                else str(last_msg)
            )

        # Build response
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid4()}",
            object="chat.completion",
            created=int(datetime.now(UTC).timestamp()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=response_content),
                    finish_reason="stop",
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=len(str(request.messages)),
                completion_tokens=len(response_content),
                total_tokens=len(str(request.messages)) + len(response_content),
            ),
        )

    except Exception as e:
        logger.error("Error in chat completion", error=str(e), model=request.model)
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


async def _stream_chat_completion(
    request: ChatCompletionRequest, graph: Any, thread_id: str, user: User
):
    """Stream chat completion responses"""
    try:
        # Convert messages to LangGraph format
        converted_messages = _convert_messages_to_langgraph_format(request.messages)

        # Build input state
        input_state = {
            "messages": converted_messages,
        }

        # Prepare config
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user.identity,
            }
        }

        # Stream the graph execution
        full_response = ""
        async for event in graph.astream_events(
            input_state, config=config, version="v2"
        ):
            event_type = event.get("event")

            # Stream LLM output events
            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk", {})
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    full_response += content

                    # Emit streaming chunk
                    choice = ChatCompletionStreamChoice(
                        index=0,
                        delta=ChatMessage(role="assistant", content=content),
                        finish_reason=None,
                    )
                    response = ChatCompletionStreamResponse(
                        id=f"chatcmpl-{uuid4()}",
                        object="chat.completion.chunk",
                        created=int(datetime.now(UTC).timestamp()),
                        model=request.model,
                        choices=[choice],
                    )
                    yield f"data: {response.model_dump_json()}\n\n"

        # Send final chunk with finish_reason
        final_choice = ChatCompletionStreamChoice(
            index=0, delta=ChatMessage(role="assistant", content=""), finish_reason="stop"
        )
        final_response = ChatCompletionStreamResponse(
            id=f"chatcmpl-{uuid4()}",
            object="chat.completion.chunk",
            created=int(datetime.now(UTC).timestamp()),
            model=request.model,
            choices=[final_choice],
        )
        yield f"data: {final_response.model_dump_json()}\n\n"

        # Send stream completion marker
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error("Error in streaming", error=str(e), model=request.model)
        error_msg = f"data: {{'error': {{'message': '{str(e)}'}}}}\n\n"
        yield error_msg


@router.get(
    "/v1/health",
    tags=["OpenAI Compatibility"],
    summary="Health check",
    response_model=dict,
)
async def openai_health_check(user: User = Depends(get_current_user)):
    """Health check endpoint for OpenAI-compatible API"""
    return {"status": "ok", "service": "aegra-openai-compat"}
