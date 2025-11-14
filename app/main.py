" FastAPI application exposing Ollama and YOLO services.

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.routers import ollama, yolo
from app.services.ollama_client import OllamaClient
from app.services.yolo_runner import YoloRunner


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.ollama_client = OllamaClient(settings.ollama_base_url)
    app.state.yolo_runner = YoloRunner(
        settings.yolo_model, confidence=settings.yolo_confidence
    )
    try:
        yield
    finally:
        await app.state.ollama_client.aclose()
        app.state.yolo_runner.close()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title=Colab Ollama + YOLO, lifespan=lifespan)

 app.add_middleware(
 CORSMiddleware,
 allow_origins=[*],
 allow_credentials=True,
 allow_methods=[*],
 allow_headers=[*],
 )

 @app.get(/hello)
 async def hello_world() -> dict[str, str]:
 Simple endpoint for smoke tests.

        return {message: hello world}

 app.include_router(ollama.router)
 app.include_router(yolo.router)

 return app


app = create_app()
