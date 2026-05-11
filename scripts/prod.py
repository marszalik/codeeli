"""Production entrypoint for codeeli.

Reads HOST (default 127.0.0.1) and PORT (default 3004) from the environment.
No reload, no extra workers.
"""
import os
import sys
from pathlib import Path

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "3004"))
    print(f"Codeeli prod on http://{host}:{port}", flush=True)
    uvicorn.run("app.main:app", host=host, port=port, log_level="info", access_log=True)


if __name__ == "__main__":
    main()
