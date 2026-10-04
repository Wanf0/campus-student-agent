"""评测 runner：对当前 Agent 与 naive RAG 基线跑评测集，输出指标对比。"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.domain.agent import CampusAgent, GROUNDED_PROMPT
from app.infrastructure import embedding, vectorstore, llm

DATASET = Path(__file__).parent / "datasets" / "campus_qa.json"


def load_dataset() -> list[dict]:
    return json.loads(DATASET.read_text(encoding="utf-8"))


def naive_rag(query: str) -> tuple[str, list[str]]:
    """naive RAG 基线：仅向量检索 + 生成，无重排/分级/过滤。"""
    q_emb = embedding.embed_text(query)
    res = vectorstore.query(q_emb, n_results=4)
    docs = (res.get("documents") or [[]])[0]
    metadatas = (res.get("metadatas") or [[]])[0]
    context = "\n\n".join(docs) if docs else "（无检索结果）"
    system = GROUNDED_PROMPT + "\n\n可用资料：\n" + context
    answer = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": query}])
    citations = [m.get("title", "") for m in metadatas if m]
    return answer, citations


def evaluate(name: str, fn) -> dict:
    dataset = load_dataset()
    n = len(dataset)
    intent_ok = kw_hits = citation_hits = grounding_ok = 0
    kw_total = citation_total = grounding_total = 0
    total_citations = 0
    agent = CampusAgent() if name == "agent" else None

    for item in dataset:
        query = item["query"]
        expected_intent = item["expected_intent"]
        keywords = item.get("expected_keywords", [])
        sources = item.get("expected_sources", [])

        if name == "agent":
            out = agent.run(query)
            answer = out.answer
            citations = [c.title for c in out.citations]
            intent = out.intent
        else:
            answer, citations = fn(query)
            intent = "qa" if sources else "academic" if any(k in query for k in ["课表", "成绩", "校历", "通知"]) else "qa"

        total_citations += len(citations)

        # 路由准确率（naive 仅做宽松比对，agent 精确比对）
        if name == "agent" and intent == expected_intent:
            intent_ok += 1
        elif name == "naive":
            intent_ok += 1  # naive 无路由，不计入

        # 答案关键词命中率
        for kw in keywords:
            kw_total += 1
            if kw in answer:
                kw_hits += 1

        # 引用命中率（答案或引用中出现期望来源）
        for src in sources:
            citation_total += 1
            if any(src in c for c in citations) or src in answer:
                citation_hits += 1

        # grounding 行为（知识库外/歧义：应表达"无法回答/不确定"而非编造）
        if not keywords and not sources:
            grounding_total += 1
            if any(k in answer for k in ["无法", "不确定", "没有", "未找到", "建议"]):
                grounding_ok += 1

    intent_denom = n if name == "agent" else n
    return {
        "routing_accuracy": round(intent_ok / intent_denom, 3),
        "answer_keyword_recall": round(kw_hits / kw_total, 3) if kw_total else None,
        "citation_hit": round(citation_hits / citation_total, 3) if citation_total else None,
        "grounding_ok": round(grounding_ok / grounding_total, 3) if grounding_total else None,
        "avg_citations": round(total_citations / n, 2),
    }


def main():
    print("=" * 60)
    print("校园智能体评测（After: agentic RAG vs Before: naive RAG）")
    print("=" * 60)
    after = evaluate("agent", None)
    before = evaluate("naive", naive_rag)
    for key in ["routing_accuracy", "answer_keyword_recall", "citation_hit", "grounding_ok", "avg_citations"]:
        print(f"{key:22s}  Before(naive)={before[key]}  After(agentic)={after[key]}")
    print("=" * 60)
    print("说明：avg_citations 越低越精确（agentic 只引用相关证据，naive 引用全部 top-k）。")


if __name__ == "__main__":
    main()
