from fastapi import FastAPI

from .config import settings
from .schemas import ChatRequest, ChatResponse
from .services import llm

app = FastAPI(title="校园学生智能体", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.deepseek_model}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    messages = [
        {
            "role": "system",
            "content": "你是一个校园学生智能体，为学生提供校园信息、学习辅导等服务。回答简洁、友好。",
        },
        {"role": "user", "content": req.message},
    ]
    reply = llm.chat(messages)
    return ChatResponse(reply=reply, conversation_id=req.conversation_id, intent="general")
