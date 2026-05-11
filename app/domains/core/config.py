from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
WORKSPACES_DIR = BASE_DIR / "workspaces"
DB_PATH = DATA_DIR / "codeeli.sqlite3"
STATIC_DIR = APP_DIR / "domains" / "core" / "static"


def ensure_runtime_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
