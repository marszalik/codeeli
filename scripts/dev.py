import socket
import sys
from pathlib import Path

import uvicorn


HOST = "0.0.0.0"
START_PORT = 8000
PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))


def first_free_port(start_port: int = START_PORT) -> int:
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((HOST, port))
            except OSError:
                port += 1
                continue
            return port
    raise RuntimeError("No free TCP port found.")


if __name__ == "__main__":
    port = first_free_port()
    print(f"Starting Codeeli on http://{HOST}:{port}")
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=port,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT)],
    )
