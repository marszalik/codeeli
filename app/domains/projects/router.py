from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domains.ai_settings.service import list_configs
from app.domains.core.templates import render
from app.domains.generation.repository import latest_state
from app.domains.projects import service
from app.domains.recipes.service import list_recipes


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_class=HTMLResponse)
def index() -> bytes:
    projects = service.list_projects()
    return render(
        "projects/index.mako",
        projects=projects,
        recipes=list_recipes(),
        configs=list_configs(),
        active="projects",
    )


@router.get("/{project_id}", response_class=HTMLResponse)
def detail(project_id: int) -> bytes:
    project = service.get_project(project_id)
    return render(
        "projects/detail.mako",
        project=project,
        generation_state=latest_state(project_id),
        recipes=list_recipes(),
        configs=list_configs(),
        active="projects",
    )


@router.post("")
def create(
    name: str = Form(...),
    recipe_id: int = Form(...),
    ai_config_id: int = Form(...),
    workspace_dir: str = Form(""),
    prompt: str = Form(""),
) -> RedirectResponse:
    service.create_project(name, recipe_id, ai_config_id, workspace_dir, prompt)
    return RedirectResponse("/projects", status_code=303)


@router.post("/{project_id}")
def update(
    project_id: int,
    name: str = Form(...),
    recipe_id: int = Form(...),
    ai_config_id: int = Form(...),
    workspace_dir: str = Form(""),
    prompt: str = Form(""),
) -> RedirectResponse:
    service.update_project(project_id, name, recipe_id, ai_config_id, workspace_dir, prompt)
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@router.post("/{project_id}/delete")
def delete(project_id: int) -> RedirectResponse:
    service.delete_project(project_id)
    return RedirectResponse("/projects", status_code=303)
