"""FastAPI routes for interacting with Ollama."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from httpx import HTTPError

from app.config import Settings, get_settings
from app.schemas.ollama import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    GenerateRequest,
    GenerateResponse,
)
from app.services.ollama_client import OllamaClient


router = APIRouter(prefix="/ollama", tags=["ollama"])


async def get_ollama_client(request: Request) -> OllamaClient:
    client: OllamaClient | None = getattr(request.app.state, "ollama_client", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama client is not initialized.",
        )
    return client


SettingsDep = Annotated[Settings, Depends(get_settings)]
ClientDep = Annotated[OllamaClient, Depends(get_ollama_client)]


@router.post(
    "/generate",
    response_model=GenerateResponse,
    responses={502: {"model": ErrorResponse}},
)
async def generate(
    payload: GenerateRequest,
    client: ClientDep,
    settings: SettingsDep,
) -> GenerateResponse:
    model = payload.model or settings.ollama_model
    try:
        response = await client.generate(
            model=model,
            prompt=payload.prompt,
            options=payload.options,
        )
    except HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama generate failed: {exc}",
        ) from exc
    return GenerateResponse(**response)


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={502: {"model": ErrorResponse}},
)
async def chat(
    payload: ChatRequest,
    client: ClientDep,
    settings: SettingsDep,
) -> ChatResponse:
    model = payload.model or settings.ollama_model
    try:
        response = await client.chat(
            model=model,
            messages=[message.model_dump() for message in payload.messages],
            options=payload.options,
        )
    except HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama chat failed: {exc}",
        ) from exc
    return ChatResponse(**response)
