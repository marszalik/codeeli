from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter()


@router.get("/")
def home() -> RedirectResponse:
    return RedirectResponse("/projects", status_code=302)
