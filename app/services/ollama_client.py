"""Async client wrapper around the local Ollama HTTP API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx


class OllamaClient:
    """Provide thin async helpers over the Ollama REST endpoints."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 120.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers=headers,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def generate(
        self,
        *,
        model: str,
        prompt: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"model": model, "prompt": prompt}
        if options:
            payload["options"] = options
        return await self._post("/api/generate", payload)

    async def chat(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"model": model, "messages": messages}
        if options:
            payload["options"] = options
        return await self._post("/api/chat", payload)

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = await self._client.post(path, json=payload)
        response.raise_for_status()
        return response.json()
