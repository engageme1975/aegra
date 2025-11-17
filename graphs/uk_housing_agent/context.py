"""Configurable parameters for the UK Housing Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from typing import Annotated


@dataclass(kw_only=True)
class Context:
    """Configuration context for the UK Housing Agent."""

    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", ""),
        metadata={"description": "OpenAI API key for LLM access"}
    )

    openai_api_base: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        metadata={"description": "OpenAI API base URL"}
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        metadata={"description": "LLM model to use (provider/model-name)"}
    )

    temperature: float = field(
        default=0.7,
        metadata={"description": "Temperature for model generation (0.0-1.0)"}
    )

    max_tokens: int = field(
        default=1000,
        metadata={"description": "Maximum tokens to generate per response"}
    )

    # OpenSearch for RAG
    opensearch_host: str = field(
        default_factory=lambda: os.getenv("OPENSEARCH_HOST", ""),
        metadata={"description": "OpenSearch host for RAG knowledge base"}
    )

    opensearch_port: int = field(
        default=25060,
        metadata={"description": "OpenSearch port"}
    )

    opensearch_user: str = field(
        default_factory=lambda: os.getenv("OPENSEARCH_USER", ""),
        metadata={"description": "OpenSearch username"}
    )

    opensearch_password: str = field(
        default_factory=lambda: os.getenv("OPENSEARCH_PASSWORD", ""),
        metadata={"description": "OpenSearch password"}
    )

    # LangSmith tracing
    langsmith_api_key: str = field(
        default_factory=lambda: os.getenv("LANGSMITH_API_KEY", ""),
        metadata={"description": "LangSmith API key for tracing (optional)"}
    )

    langsmith_project: str = field(
        default_factory=lambda: os.getenv("LANGSMITH_PROJECT", "uk-housing-agent"),
        metadata={"description": "LangSmith project name"}
    )

    def __post_init__(self) -> None:
        """Fetch environment variables for attributes not explicitly passed."""
        for f in fields(self):
            if not f.init:
                continue
            # If using default factory, it already loaded from env
            # No need to override further
