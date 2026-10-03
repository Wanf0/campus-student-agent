from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Conversation, Message
from ..schemas import ChatRequest, ChatResponse
from ..services import agent_runner

router = APIRouter(tags=["对话"])

HISTORY_LIMIT = 10


@router.get("/conversations")
def list_conversations(user_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Conversation).order_by(Conversation.updated_at.desc())
    if user_id is not None:
        q = q.filter(Conversation.user_id == user_id)
    convs = q.all()
    return [{"id": c.id, "title": c.title, "user_id": c.user_id} for c in convs]


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.asc())
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in msgs]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    conversation_id = req.conversation_id
    history: list[dict] = []

    if conversation_id:
        msgs = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.id.desc())
            .limit(HISTORY_LIMIT)
            .all()
        )
        history = [{"role": m.role, "content": m.content} for m in reversed(msgs)]
    else:
        conv = Conversation(user_id=req.user_id or 1, title=req.message[:20])
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id

    reply, intent = agent_runner.run(req.message, history)

    db.add(Message(conversation_id=conversation_id, role="user", content=req.message))
    db.add(Message(conversation_id=conversation_id, role="assistant", content=reply))
    conv = db.get(Conversation, conversation_id)
    if conv:
        conv.updated_at = datetime.utcnow()
    db.commit()

    return ChatResponse(reply=reply, conversation_id=conversation_id, intent=intent)
