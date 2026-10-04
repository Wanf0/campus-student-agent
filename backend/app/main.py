import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, chat, admin
from app.config import settings
from app.domain.models import Base
from app.infrastructure.db import engine

Base.metadata.create_all(bind=engine)

FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(title="校园学生智能体", version="0.4.0")

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.deepseek_model}
