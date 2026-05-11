from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domains.core.templates import render
from app.domains.instructions import service


router = APIRouter(prefix="/instructions", tags=["instructions"])


@router.get("", response_class=HTMLResponse)
def index() -> bytes:
    return render("instructions/index.mako", instructions=service.list_instructions(), active="instructions")


@router.post("/{item_id}")
def update(item_id: int, title: str = Form(...), content: str = Form(...)) -> RedirectResponse:
    service.update_instruction(item_id, title, content)
    return RedirectResponse("/instructions", status_code=303)
