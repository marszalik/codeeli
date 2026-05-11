from fastapi import APIRouter, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse

from app.domains.generation.repository import latest_state
from app.domains.generation.service import (
    generate_project,
    launch_url,
    run_project_command,
    safe_project_path,
)
from app.domains.projects.service import get_project_details


router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/projects/{project_id}")
async def generate(project_id: int, prompt: str = Form(...)) -> StreamingResponse:
    return StreamingResponse(generate_project(project_id, prompt), media_type="text/event-stream")


@router.get("/projects/{project_id}/state")
def state(project_id: int) -> dict:
    return latest_state(project_id)


@router.post("/projects/{project_id}/launch")
def launch(project_id: int) -> JSONResponse:
    try:
        return JSONResponse({"url": launch_url(project_id)})
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)


@router.get("/projects/{project_id}/workspace/{filename:path}")
def workspace_file(project_id: int, filename: str) -> FileResponse:
    project = get_project_details(project_id)
    if not project:
        raise RuntimeError("Project not found.")
    target = safe_project_path(project["workspace_dir"], filename)
    return FileResponse(target)


@router.get("/projects/{project_id}/run", response_class=HTMLResponse)
async def run(project_id: int) -> str:
    return await run_project_command(project_id)
