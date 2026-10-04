import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, chat, admin
from app.config import settings
from app.domain.models import Base
from app.infrastructure.db import engine

Base.metadata.create_all(bind=engine)

FRONTEND_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent / "frontend"
DIST_DIR = FRONTEND_ROOT / "dist"

app = FastAPI(title="校园学生智能体", version="0.4.0")

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)

# 生产模式：服务 Vite 构建产物（frontend/dist）；开发模式用 `npm run dev` 代理
if (DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")


@app.get("/")
def index():
    index_file = DIST_DIR / "index.html" if (DIST_DIR / "index.html").exists() else FRONTEND_ROOT / "index.html"
    return FileResponse(index_file)


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.deepseek_model}
