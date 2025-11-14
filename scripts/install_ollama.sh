#!/usr/bin/env bash
set -euo pipefail

# Ensure we run from the script's directory
dirname "${BASH_SOURCE[0]}" >/dev/null 2>&1

if ! command -v curl >/dev/null 2>&1; then
  echo "[install_ollama] Installing curl..."
  sudo apt-get update && sudo apt-get install -y curl
fi

echo "[install_ollama] Downloading Ollama installer..."
curl -fsSL https://ollama.com/install.sh | sh

if pgrep -f "ollama serve" >/dev/null 2>&1; then
  echo "[install_ollama] Ollama already running. Skipping start."
else
  echo "[install_ollama] Starting Ollama daemon..."
  OLLAMA_HOST="0.0.0.0" OLLAMA_PORT=${OLLAMA_PORT:-11434} nohup ollama serve >/tmp/ollama.log 2>&1 &
  sleep 2
  echo "[install_ollama] Ollama logs → /tmp/ollama.log"
fi

if [[ -n "${OLLAMA_MODEL:-}" ]]; then
  echo "[install_ollama] Pulling model ${OLLAMA_MODEL}..."
  ollama pull "${OLLAMA_MODEL}"
fi

echo "[install_ollama] Done."
