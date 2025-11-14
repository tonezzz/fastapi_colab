"""Pydantic models for Ollama request/response payloads."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(description="Chat role, e.g. 'user' or 'assistant'.")
    content: str = Field(description="Message content.")


class GenerateRequest(BaseModel):
    prompt: str = Field(description="Prompt text to send to the model.")
    model: Optional[str] = Field(
        default=None, description="Specific Ollama model to override the default."
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Advanced Ollama generation options forwarded verbatim.",
    )


class GenerateResponse(BaseModel):
    response: str
    model: str
    created_at: Optional[str] = None
    done: Optional[bool] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    total_duration: Optional[int] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    message: Message
    model: str
    created_at: Optional[str] = None
    done: Optional[bool] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    total_duration: Optional[int] = None


class ErrorResponse(BaseModel):
    detail: str
