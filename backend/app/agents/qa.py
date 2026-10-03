"""校园智能问答智能体：基于 RAG 的问答（混合检索 + 重排）。"""

from ..services import llm, retrieval, rerank

SYSTEM_PROMPT = (
    "你是校园学生智能体，负责校园信息问答。"
    "请基于给定的校园资料回答用户问题，并在回答末尾注明信息来源。"
    "如果资料不足以回答，请如实说明，不要编造校园信息。"
)

TOP_K = 4


def prepare(message: str, history: list[dict] | None = None) -> list[dict]:
    """准备用于最终生成的 messages（含检索到的上下文）。"""
    candidates = retrieval.hybrid_search(message, top_k=8)
    candidates = rerank.rerank(message, candidates)
    docs = candidates[:TOP_K]

    if docs:
        context = "\n\n".join(
            f"【来源：{c['meta'].get('title', '')}】\n{c['text']}" for c in docs
        )
        system = SYSTEM_PROMPT + "\n\n可用资料：\n" + context
    else:
        system = SYSTEM_PROMPT + "\n\n（当前知识库无相关检索结果）"

    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})
    return messages


def handle(message: str, history: list[dict] | None = None) -> str:
    return llm.chat(prepare(message, history))


def handle_stream(message: str, history: list[dict] | None = None):
    yield from llm.chat_stream(prepare(message, history))
