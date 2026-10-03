"""多智能体编排：同步走 LangGraph 工作流，流式直接分发。"""

from .. import workflow
from ..agents import router, qa, academic, generic


def _stream_dispatch(intent: str, message: str, history: list[dict] | None = None):
    if intent == "academic":
        yield from academic.handle_stream(message, history)
    elif intent in ("qa", "life"):
        yield from qa.handle_stream(message, history)
    elif intent in ("study", "psychology", "planning"):
        yield from generic.handle_stream(intent, message, history)
    else:
        yield from qa.handle_stream(message, history)


def run(message: str, history: list[dict] | None = None) -> tuple[str, str]:
    """同步执行：LangGraph 工作流编排。"""
    return workflow.run(message, history)


def run_stream(message: str, history: list[dict] | None = None) -> tuple[str, object]:
    """返回 (intent, token 生成器)。"""
    intent = router.route(message)
    if intent not in ("academic", "qa", "life", "study", "psychology", "planning"):
        intent = "qa"
    return intent, _stream_dispatch(intent, message, history)
