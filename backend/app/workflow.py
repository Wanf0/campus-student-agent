"""多智能体工作流编排：使用 LangGraph 状态图实现路由与分发。"""

from typing import TypedDict

from langgraph.graph import StateGraph, END

from .agents import router, qa, academic, generic

VALID = ("academic", "qa", "life", "study", "psychology", "planning")


class AgentState(TypedDict):
    message: str
    history: list
    intent: str
    reply: str


def _route(state: AgentState) -> dict:
    intent = router.route(state["message"])
    if intent not in VALID:
        intent = "qa"
    return {"intent": intent}


def _qa(state: AgentState) -> dict:
    return {"reply": qa.handle(state["message"], state.get("history"))}


def _academic(state: AgentState) -> dict:
    return {"reply": academic.handle(state["message"], state.get("history"))}


def _study(state: AgentState) -> dict:
    return {"reply": generic.handle("study", state["message"], state.get("history"))}


def _life(state: AgentState) -> dict:
    # 校园生活事实性问答同样走 RAG
    return {"reply": qa.handle(state["message"], state.get("history"))}


def _psychology(state: AgentState) -> dict:
    return {"reply": generic.handle("psychology", state["message"], state.get("history"))}


def _planning(state: AgentState) -> dict:
    return {"reply": generic.handle("planning", state["message"], state.get("history"))}


def _decide(state: AgentState) -> str:
    return state["intent"]


_graph = StateGraph(AgentState)
_graph.add_node("route", _route)
_graph.add_node("qa", _qa)
_graph.add_node("academic", _academic)
_graph.add_node("study", _study)
_graph.add_node("life", _life)
_graph.add_node("psychology", _psychology)
_graph.add_node("planning", _planning)
_graph.set_entry_point("route")
_graph.add_conditional_edges(
    "route",
    _decide,
    {
        "qa": "qa",
        "academic": "academic",
        "study": "study",
        "life": "life",
        "psychology": "psychology",
        "planning": "planning",
    },
)
for _n in ("qa", "academic", "study", "life", "psychology", "planning"):
    _graph.add_edge(_n, END)

compiled = _graph.compile()


def run(message: str, history: list[dict] | None = None) -> tuple[str, str]:
    result = compiled.invoke({"message": message, "history": history or []})
    return result["reply"], result["intent"]
