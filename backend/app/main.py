import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import Base, engine
from .routers import auth, chat, admin

Base.metadata.create_all(bind=engine)

FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(title="校园学生智能体", version="0.3.0")

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
