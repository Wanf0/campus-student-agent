"""多智能体编排：路由 → 领域智能体。"""

from ..agents import router, qa, academic, generic


def run(message: str, history: list[dict] | None = None) -> tuple[str, str]:
    intent = router.route(message)
    if intent == "academic":
        reply = academic.handle(message, history)
    elif intent in ("qa", "life"):
        # 校园事实性问答（制度/通知/图书馆/食堂等）统一走 RAG
        reply = qa.handle(message, history)
    elif intent in ("study", "psychology", "planning"):
        reply = generic.handle(intent, message, history)
    else:
        reply = qa.handle(message, history)
        intent = "qa"
    return reply, intent
