from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domains.core.templates import render
from app.domains.recipes import service


router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_class=HTMLResponse)
def index() -> bytes:
    return render("recipes/index.mako", recipes=service.list_recipes(), active="recipes")


@router.post("")
def create(
    name: str = Form(...),
    content: str = Form(...),
    run_command: str = Form(""),
) -> RedirectResponse:
    service.create_recipe(name, content, run_command)
    return RedirectResponse("/recipes", status_code=303)


@router.post("/{recipe_id}")
def update(
    recipe_id: int,
    name: str = Form(...),
    content: str = Form(...),
    run_command: str = Form(""),
) -> RedirectResponse:
    service.update_recipe(recipe_id, name, content, run_command)
    return RedirectResponse("/recipes", status_code=303)


@router.post("/{recipe_id}/delete")
def delete(recipe_id: int) -> RedirectResponse:
    service.delete_recipe(recipe_id)
    return RedirectResponse("/recipes", status_code=303)
