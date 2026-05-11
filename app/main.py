from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.domains.ai_settings.router import router as ai_settings_router
from app.domains.core.config import STATIC_DIR
from app.domains.core.database import init_db
from app.domains.core.router import router as core_router
from app.domains.generation.router import router as generation_router
from app.domains.instructions.router import router as instructions_router
from app.domains.projects.router import router as projects_router
from app.domains.recipes.router import router as recipes_router


app = FastAPI(title="Codeeli")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()


app.include_router(core_router)
app.include_router(ai_settings_router)
app.include_router(projects_router)
app.include_router(recipes_router)
app.include_router(instructions_router)
app.include_router(generation_router)
