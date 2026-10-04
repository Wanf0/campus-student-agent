"""应用编排：run 生命周期、trace、会话与 Agent 调度。"""

import uuid
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.agent import CampusAgent
from app.domain.entities import AgentOutput
from app.domain.models import Conversation, Message
from app.domain import memory
from app.infrastructure import observability
from app.infrastructure.observability import Timer

HISTORY_LIMIT = 10

_agent = CampusAgent()


def resolve_conversation(db: Session, user_id: int | None, message: str, conversation_id: int | None = None):
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
        conv = Conversation(user_id=user_id or 1, title=memory.generate_title(message))
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
    return conversation_id, history


def _save(db: Session, conversation_id: int, query: str, output: AgentOutput):
    db.add(Message(conversation_id=conversation_id, role="user", content=query))
    db.add(Message(conversation_id=conversation_id, role="assistant", content=output.answer))
    conv = db.get(Conversation, conversation_id)
    if conv:
        conv.updated_at = datetime.utcnow()
    db.commit()


def run(db: Session, query: str, user_id: int | None, conversation_id: int | None = None):
    run_id = uuid.uuid4().hex
    conversation_id, history = resolve_conversation(db, user_id, query, conversation_id)
    observability.new_run(db, run_id, query, user_id)

    with Timer() as t:
        output = _agent.run(query, history)

    _save(db, conversation_id, query, output)
    observability.finish_run(db, run_id, output.answer, t.elapsed_ms)
    return output, conversation_id, run_id
