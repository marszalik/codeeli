"""Production entrypoint for codeeli.

Reads host/port from environment variables set by the systemd unit:
- APP_GOOGLE_HOST or HOST (default 127.0.0.1)
- APP_GOOGLE_PORT or PORT (default 3004)

No reload, no extra workers.
"""
import os
import sys
from pathlib import Path

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    host = os.environ.get("APP_GOOGLE_HOST") or os.environ.get("HOST") or "127.0.0.1"
    port = int(os.environ.get("APP_GOOGLE_PORT") or os.environ.get("PORT") or "3004")
    print(f"Codeeli prod on http://{host}:{port}", flush=True)
    uvicorn.run("app.main:app", host=host, port=port, log_level="info", access_log=True)


if __name__ == "__main__":
    main()
