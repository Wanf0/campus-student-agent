from fastapi import FastAPI

from .config import settings
from .db import Base, engine
from .routers import auth, chat, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="校园学生智能体", version="0.2.0")

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.deepseek_model}
