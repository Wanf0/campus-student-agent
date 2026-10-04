"""可观测性：run/trace 记录与结构化日志。"""

import logging
import time

from sqlalchemy.orm import Session

from app.config import settings
from app.domain.models import Run, TraceEvent, ToolCall

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("campus.agent")


def new_run(db: Session, run_id: str, query: str, user_id: int | None) -> None:
    db.add(Run(run_id=run_id, user_id=user_id, query=query))
    db.commit()


def record_event(db: Session, run_id: str, step: str, detail: str | None = None,
                 latency_ms: int | None = None) -> None:
    db.add(TraceEvent(run_id=run_id, step=step, detail=detail, latency_ms=latency_ms))
    logger.info("run=%s step=%s %s", run_id, step, detail or "")
    db.commit()


def record_tool_call(db: Session, run_id: str, tool_name: str, category: str,
                     args: str, result: str, status: str, latency_ms: int | None) -> None:
    db.add(ToolCall(run_id=run_id, tool_name=tool_name, category=category, args=args,
                    result=result, status=status, latency_ms=latency_ms))
    logger.info("run=%s tool=%s status=%s", run_id, tool_name, status)
    db.commit()


def finish_run(db: Session, run_id: str, final_answer: str | None, latency_ms: int,
               token_usage: int | None = None, error: str | None = None) -> None:
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.final_answer = final_answer
        run.latency_ms = latency_ms
        run.token_usage = token_usage
        run.error = error
        db.commit()


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = int((time.perf_counter() - self.start) * 1000)
