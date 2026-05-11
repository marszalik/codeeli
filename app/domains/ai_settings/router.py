from fastapi import APIRouter, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.domains.ai_settings import service
from app.domains.core.templates import render


router = APIRouter(prefix="/ai-settings", tags=["ai-settings"])


@router.get("", response_class=HTMLResponse)
def index() -> bytes:
    return render("ai_settings/index.mako", configs=service.list_configs(), active="ai")


@router.post("")
def create(
    name: str = Form(...),
    provider: str = Form(...),
    base_url: str = Form(""),
    api_key: str = Form(""),
    model: str = Form(...),
    temperature: float = Form(0),
) -> RedirectResponse:
    service.create_config(
        {
            "name": name,
            "provider": provider,
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
            "temperature": temperature,
        }
    )
    return RedirectResponse("/ai-settings", status_code=303)


@router.post("/{config_id}/delete")
def delete(config_id: int) -> RedirectResponse:
    service.delete_config(config_id)
    return RedirectResponse("/ai-settings", status_code=303)


@router.get("/models")
async def models(
    provider: str = Query(...),
    base_url: str = Query(""),
    api_key: str = Query(""),
) -> JSONResponse:
    try:
        return JSONResponse({"models": await service.list_models(provider, base_url, api_key)})
    except Exception as exc:
        return JSONResponse({"models": [], "error": str(exc)}, status_code=200)
