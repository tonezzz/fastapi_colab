"""Utility script to generate the Colab workflow notebook."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


def main() -> None:
    nb = nbf.v4.new_notebook()

    cells = [
        nbf.v4.new_markdown_cell(
            """# Colab FastAPI + Ollama + YOLO\n\n"
            "This notebook provisions the FastAPI project, installs Ollama/YOLO, and exposes the API via ngrok.\n"
            "Run the cells top-to-bottom whenever you need a fresh Colab runtime."""
        ),
        nbf.v4.new_markdown_cell(
            """## Before you run\n"
            "1. Upload this repository (or sync from Git) into `/content/colab_fastapi`.\n"
            "2. (Optional) Add your ngrok authtoken to the Colab secrets manager and set `NGROK_AUTHTOKEN`.\n"
            "3. Decide which Ollama + YOLO models you want to use; defaults are `phi3` and `yolov8n.pt`."""
        ),
        nbf.v4.new_code_cell(
            """from pathlib import Path\nimport os\n\nPROJECT_ROOT = Path('/content/colab_fastapi').resolve()\nif not PROJECT_ROOT.exists():\n    raise RuntimeError('Upload the project into /content/colab_fastapi before continuing.')\n\nos.chdir(PROJECT_ROOT)\nprint('Working directory:', PROJECT_ROOT)"""
        ),
        nbf.v4.new_code_cell(
            """import os\n\nos.environ.setdefault('FASTAPI_PORT', '8000')\nos.environ.setdefault('OLLAMA_MODEL', 'phi3')\nos.environ.setdefault('YOLO_MODEL', 'yolov8n.pt')\nos.environ.setdefault('YOLO_CONFIDENCE', '0.35')\n\nprint('FASTAPI_PORT =', os.environ['FASTAPI_PORT'])\nprint('OLLAMA_MODEL =', os.environ['OLLAMA_MODEL'])\nprint('YOLO_MODEL =', os.environ['YOLO_MODEL'])\nprint('YOLO_CONFIDENCE =', os.environ['YOLO_CONFIDENCE'])\nprint('NGROK_AUTHTOKEN =', os.environ.get('NGROK_AUTHTOKEN', '<unset>'))"""
        ),
        nbf.v4.new_code_cell(
            """%%bash\ncd /content/colab_fastapi\nsudo apt-get update -y\nsudo apt-get install -y curl git\npip install --upgrade pip\npip install -r requirements.txt"""
        ),
        nbf.v4.new_code_cell(
            """%%bash\ncd /content/colab_fastapi\nchmod +x scripts/install_ollama.sh\nexport OLLAMA_MODEL=${OLLAMA_MODEL:-phi3}\nexport OLLAMA_PORT=${OLLAMA_PORT:-11434}\nscripts/install_ollama.sh"""
        ),
        nbf.v4.new_code_cell(
            """import asyncio\nimport os\nimport threading\nimport time\n\nimport uvicorn\n\nFASTAPI_PORT = int(os.environ['FASTAPI_PORT'])\n\nif 'SERVER_THREAD' in globals():\n    print('FastAPI server already running.')\nelse:\n    config = uvicorn.Config('app.main:app', host='0.0.0.0', port=FASTAPI_PORT, log_level='info')\n    server = uvicorn.Server(config)\n\n    def _run_server():\n        asyncio.run(server.serve())\n\n    SERVER_THREAD = threading.Thread(target=_run_server, daemon=True)\n    SERVER_THREAD.start()\n    time.sleep(3)\n    print(f'FastAPI server started on port {FASTAPI_PORT}.')"""
        ),
        nbf.v4.new_code_cell(
            """import os\n\nfrom scripts.start_ngrok import start_ngrok\n\npublic_url = start_ngrok(port=int(os.environ['FASTAPI_PORT']), authtoken=os.environ.get('NGROK_AUTHTOKEN'))\npublic_url"""
        ),
        nbf.v4.new_code_cell(
            """import asyncio\nimport base64\nimport io\nimport os\n\nimport cv2\nimport httpx\nimport numpy as np\n\nFASTAPI_ROOT = f\"http://127.0.0.1:{os.environ['FASTAPI_PORT']}\"\n\nasync def run_smoke_tests():\n    async with httpx.AsyncClient(timeout=120) as client:\n        gen_payload = {\n            'prompt': 'Say hello from the Colab FastAPI service.',\n            'model': os.environ.get('OLLAMA_MODEL'),\n        }\n        gen_resp = await client.post(f'{FASTAPI_ROOT}/ollama/generate', json=gen_payload)\n        gen_resp.raise_for_status()\n        print('Ollama /generate →', gen_resp.json())\n\n        dummy = np.zeros((320, 320, 3), dtype=np.uint8)\n        cv2.putText(dummy, 'COLAB', (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)\n        success, buffer = cv2.imencode('.jpg', dummy)\n        if not success:\n            raise RuntimeError('Failed to encode dummy image.')\n        files = {'file': ('dummy.jpg', buffer.tobytes(), 'image/jpeg')}\n        detect_resp = await client.post(f'{FASTAPI_ROOT}/yolo/detect', files=files)\n        detect_resp.raise_for_status()\n        print('YOLO /detect →', detect_resp.json())\n\nasyncio.run(run_smoke_tests())"""
        ),
        nbf.v4.new_markdown_cell(
            """### Cleanup\nRun the cell below when you need to stop the server and ngrok tunnel."""
        ),
        nbf.v4.new_code_cell(
            """import asyncio\n\nif 'server' in globals():\n    asyncio.run(server.shutdown())\n    print('FastAPI server shutdown requested.')\nif 'SERVER_THREAD' in globals():\n    SERVER_THREAD.join(timeout=5)\n    print('Server thread joined.')\n\nfrom pyngrok import ngrok\nngrok.kill()\nprint('ngrok tunnel closed.')"""
        ),
    ]

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10",
        },
    }

    notebooks_dir = Path("notebooks")
    notebooks_dir.mkdir(parents=True, exist_ok=True)
    target = notebooks_dir / "fastapi_ollama_yolo.ipynb"
    with target.open("w", encoding="utf-8") as fp:
        nbf.write(nb, fp)
    print(f"Notebook written to {target}")


if __name__ == "__main__":
    main()
