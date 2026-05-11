from pathlib import Path

from app.domains.core.config import WORKSPACES_DIR
from app.domains.projects import repository


def list_projects() -> list[dict]:
    return repository.list_projects()


def get_project(project_id: int) -> dict | None:
    return repository.get_project(project_id)


def get_project_details(project_id: int) -> dict | None:
    return repository.get_project_details(project_id)


def normalize_workspace_dir(value: str, name: str) -> str:
    if value.strip():
        return str(Path(value).expanduser())
    slug = "".join(char.lower() if char.isalnum() else "-" for char in name).strip("-") or "project"
    return str(WORKSPACES_DIR / slug)


def create_project(name: str, recipe_id: int, ai_config_id: int, workspace_dir: str, prompt: str) -> None:
    repository.create_project(name, recipe_id, ai_config_id, normalize_workspace_dir(workspace_dir, name), prompt)


def update_project(project_id: int, name: str, recipe_id: int, ai_config_id: int, workspace_dir: str, prompt: str) -> None:
    repository.update_project(project_id, name, recipe_id, ai_config_id, normalize_workspace_dir(workspace_dir, name), prompt)


def delete_project(project_id: int) -> None:
    repository.delete_project(project_id)
