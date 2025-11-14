"""Application configuration utilities."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    fastapi_host: str = Field(
        default="0.0.0.0",
        description="Host interface for the FastAPI server",
    )
    fastapi_port: int = Field(
        default=8000,
        description="Port number for the FastAPI server",
    )
    ollama_host: str = Field(
        default="127.0.0.1",
        description="Hostname where the Ollama daemon listens",
    )
    ollama_port: int = Field(default=11434, description="Port for the Ollama API")
    ollama_model: str = Field(
        default="phi3",
        description="Default Ollama model when none is supplied",
    )
    yolo_model: str = Field(
        default="yolov8n.pt",
        description="Ultralytics YOLO weights identifier to load at startup",
    )
    yolo_confidence: float = Field(
        default=0.35,
        description="Default confidence threshold for YOLO detections",
        ge=0.0,
        le=1.0,
    )
    ngrok_authtoken: Optional[str] = Field(
        default=None,
        description="Optional ngrok auth token used by helper scripts",
    )

    @property
    def ollama_base_url(self) -> str:
        """Convenience accessor for the Ollama HTTP endpoint."""

        return f"http://{self.ollama_host}:{self.ollama_port}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance for dependency injection."""

    return Settings()
