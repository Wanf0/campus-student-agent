"""校园智能问答智能体：基于 RAG 的问答。"""

from ..services import rag, embedding, llm

SYSTEM_PROMPT = (
    "你是校园学生智能体，负责校园信息问答。"
    "请基于给定的校园资料回答用户问题，并在回答末尾注明信息来源。"
    "如果资料不足以回答，请如实说明，不要编造校园信息。"
)


def handle(message: str, history: list[dict] | None = None) -> str:
    q_emb = embedding.embed_text(message)
    res = rag.query(q_emb, n_results=4)
    docs = (res.get("documents") or [[]])[0]
    metadatas = (res.get("metadatas") or [[]])[0]

    if docs:
        context = "\n\n".join(f"【来源：{m.get('title', '')}】\n{d}" for d, m in zip(docs, metadatas))
        system = SYSTEM_PROMPT + "\n\n可用资料：\n" + context
    else:
        system = SYSTEM_PROMPT + "\n\n（当前知识库无相关检索结果）"

    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})
    return llm.chat(messages)
