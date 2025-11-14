"""Helper to start an ngrok tunnel and print the public URL."""

from __future__ import annotations

import os
from typing import Optional

from pyngrok import ngrok


def start_ngrok(port: int = 8000, authtoken: Optional[str] = None) -> str:
    if authtoken:
        ngrok.set_auth_token(authtoken)
    tunnel = ngrok.connect(port, "http")
    public_url = tunnel.public_url
    print(f"[ngrok] Public URL: {public_url}")
    return public_url


def main() -> None:
    port = int(os.environ.get("FASTAPI_PORT", 8000))
    authtoken = os.environ.get("NGROK_AUTHTOKEN")
    start_ngrok(port, authtoken)


if __name__ == "__main__":
    main()
