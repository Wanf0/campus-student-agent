"""知识检索工具（Knowledge Tool）：走权威感知 RAG 管线。"""

from app.domain.entities import Evidence
from app.domain.rag import grounding, retrieval
from app.domain.tools.base import Tool


def _search(args: dict) -> list[dict]:
    query = args.get("query", "")
    if not query:
        return []
    evidence = retrieval.hybrid_search(query)
    evidence = grounding.rerank_evidence(query, evidence)
    evidence = grounding.top_k_evidence(evidence)
    return [e.model_dump() for e in evidence]


def build_knowledge_tool() -> Tool:
    return Tool(
        "search_knowledge",
        "在校园知识库中检索与问题相关的权威、时效性资料，用于回答校园制度、通知、办事流程等问题。",
        "knowledge",
        "read_only",
        {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "检索查询"}},
            "required": ["query"],
        },
        _search,
    )


def search_knowledge(query: str) -> list[Evidence]:
    """供 Agent 直接调用的检索入口。"""
    evidence = retrieval.hybrid_search(query)
    evidence = grounding.rerank_evidence(query, evidence)
    return grounding.top_k_evidence(evidence)
