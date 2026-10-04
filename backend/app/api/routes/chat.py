import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.schemas import ChatRequest, ChatResponse, Citation
from app.application import orchestrator
from app.domain.agent import CampusAgent
from app.domain.models import Conversation, Message
from app.infrastructure import observability
from app.infrastructure.db import get_db, SessionLocal

router = APIRouter(tags=["对话"])

_agent = CampusAgent()


def _resolve(db: Session, req: ChatRequest):
    return orchestrator.resolve_conversation(db, req.user_id, req.message, req.conversation_id)


@router.get("/conversations")
def list_conversations(user_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Conversation).order_by(Conversation.updated_at.desc())
    if user_id is not None:
        q = q.filter(Conversation.user_id == user_id)
    return [{"id": c.id, "title": c.title, "user_id": c.user_id} for c in q.all()]


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.id.asc()).all()
    return [{"role": m.role, "content": m.content} for m in msgs]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    output, conversation_id, _ = orchestrator.run(db, req.message, req.user_id, req.conversation_id)
    citations = [Citation(title=c.title, authority=c.authority, publish_date=c.publish_date) for c in output.citations]
    return ChatResponse(reply=output.answer, conversation_id=conversation_id, intent=output.intent, citations=citations)


@router.post("/chat/stream")
def chat_stream(req: ChatRequest, db: Session = Depends(get_db)):
    conversation_id, history = _resolve(db, req)
    run_id = uuid.uuid4().hex
    observability.new_run(db, run_id, req.message, req.user_id)

    def event_stream():
        full = ""
        try:
            for event in _agent.run_stream(req.message, history):
                event["run_id"] = run_id
                if event["event"] == "start":
                    event["conversation_id"] = conversation_id
                if event["event"] == "token":
                    full += event.get("content", "")
                yield _sse(event)
        except Exception:
            yield _sse({"event": "error", "message": "生成过程中出错，请重试", "retryable": True, "run_id": run_id})
            yield _sse({"event": "done", "citations": [], "conversation_id": conversation_id, "run_id": run_id})

        s = SessionLocal()
        try:
            s.add(Message(conversation_id=conversation_id, role="user", content=req.message))
            s.add(Message(conversation_id=conversation_id, role="assistant", content=full))
            conv = s.get(Conversation, conversation_id)
            if conv:
                conv.updated_at = datetime.utcnow()
            s.commit()
        finally:
            s.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"
