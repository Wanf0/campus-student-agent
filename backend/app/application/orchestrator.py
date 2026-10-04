"""应用编排：run 生命周期、trace、会话与 Agent 调度。"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain import clarification, memory, router
from app.domain.agent import CampusAgent
from app.domain.clarification import PendingClarification
from app.domain.entities import AgentOutput
from app.domain.models import Conversation, Message
from app.infrastructure import observability
from app.infrastructure.observability import Timer

HISTORY_LIMIT = 10

_agent = CampusAgent()


def resolve_pending(conversation_id: int | None, query: str) -> dict | None:
    """返回待处理澄清（若存在且用户未开启新话题）。"""
    if conversation_id is None:
        return None
    pending = clarification.clarification_store.get(conversation_id)
    if pending is None:
        return None
    # 若用户输入命中其它确定意图关键词，视为放弃澄清，走普通路由
    if router.route_keyword(query) is not None:
        clarification.clarification_store.clear(conversation_id)
        return None
    return {"intent": pending.intent, "pending_tool": pending.pending_tool,
            "missing_params": pending.missing_params}


def update_pending(conversation_id: int | None, clarification_out: dict | None) -> None:
    if conversation_id is None:
        return
    if clarification_out and clarification_out.get("tool"):
        clarification.clarification_store.set(conversation_id, PendingClarification(
            intent=clarification_out.get("intent", "academic"),
            pending_tool=clarification_out.get("tool"),
            missing_params=clarification_out.get("missing_params", []),
        ))
    else:
        clarification.clarification_store.clear(conversation_id)


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

    pending = resolve_pending(conversation_id, query)
    with Timer() as t:
        output = _agent.run(query, history, clarification=pending)

    update_pending(conversation_id, output.clarification)
    _save(db, conversation_id, query, output)
    observability.finish_run(db, run_id, output.answer, t.elapsed_ms)
    return output, conversation_id, run_id
