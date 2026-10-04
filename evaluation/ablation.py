"""A-F 消融：比较各检索/生成配置在评测集上的表现。

A naive vector / B hybrid / C hybrid+rerank / D +authority / E +temporal / F +self-correction
D、E 因语料无权威/时间元数据标记为 Pending Corpus。
"""

import json
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import settings
from app.domain.agent import CampusAgent, GROUNDED_PROMPT
from app.domain.rag import grounding
from app.domain.rag.retrieval import RetrievalConfig, vector_search, hybrid_search
from app.infrastructure import llm

DATASET = Path(__file__).parent / "datasets" / "campus_qa.json"


def _rag_answer(query: str, evidence, use_self_correction: bool) -> tuple[str, list[str]]:
    if not use_self_correction:
        evidence = evidence[: settings.final_top_k]
    context = grounding.build_grounded_context(evidence) if evidence else "（无相关检索结果）"
    system = GROUNDED_PROMPT + "\n\n可用资料：\n" + context
    answer = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": query}])
    return answer, [e.source_title for e in evidence]


def run_config(name: str, dataset: list[dict]) -> dict:
    t0 = time.time()
    ret_recall_num = ret_recall_den = 0
    kw_num = kw_den = 0
    abst_num = abst_den = 0
    total_cited = 0

    agent = CampusAgent() if name == "F" else None

    for item in dataset:
        query = item["query"]
        gold = set(item.get("gold_documents", []))
        kws = item.get("expected_keywords", [])
        answerable = item.get("answerable_from_corpus", "A")

        if name == "A":
            evidence = vector_search(query, settings.retrieval_top_k)
            answer, cited = _rag_answer(query, evidence, use_self_correction=False)
        elif name == "B":
            evidence = hybrid_search(query, config=RetrievalConfig(use_bm25=True, use_authority=False, use_temporal=False))
            answer, cited = _rag_answer(query, evidence, use_self_correction=False)
        elif name == "C":
            evidence = hybrid_search(query, config=RetrievalConfig(use_bm25=True, use_authority=False, use_temporal=False))
            evidence = grounding.rerank_evidence(query, evidence)
            answer, cited = _rag_answer(query, evidence, use_self_correction=False)
        elif name == "D":
            evidence = hybrid_search(query, config=RetrievalConfig(use_bm25=True, use_authority=True, use_temporal=False))
            answer, cited = _rag_answer(query, evidence, use_self_correction=False)
        elif name == "E":
            evidence = hybrid_search(query, config=RetrievalConfig(use_bm25=True, use_authority=True, use_temporal=True))
            answer, cited = _rag_answer(query, evidence, use_self_correction=False)
        else:  # F
            out = agent.run(query)
            answer = out.answer
            cited = [c.title for c in out.citations]

        retrieved = {e.source_title for e in evidence} if name != "F" else {c for c in cited}
        # F 的 retrieved 无法直接获得，用 cited 近似（已在 agent 内部过滤）

        if gold:
            ret_recall_num += len(gold & retrieved)
            ret_recall_den += len(gold)
        for kw in kws:
            kw_den += 1
            if kw in answer:
                kw_num += 1
        if answerable == "C":
            abst_den += 1
            if any(k in answer for k in ["无法", "不确定", "没有", "未找到", "建议"]):
                abst_num += 1
        total_cited += len(cited)

    latency = round(time.time() - t0, 1)
    return {
        "config": name,
        "retrieval_recall": round(ret_recall_num / ret_recall_den, 3) if ret_recall_den else None,
        "answer_keyword_recall": round(kw_num / kw_den, 3) if kw_den else None,
        "abstention_accuracy": round(abst_num / abst_den, 3) if abst_den else None,
        "avg_citations": round(total_cited / len(dataset), 2),
        "latency_s": latency,
    }


def main():
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    print("=" * 90)
    print("A-F 消融结果")
    print("=" * 90)
    header = f"{'配置':30s} {'RetrRecall':10s} {'AnsRecall':9s} {'Abstention':10s} {'avgCit':7s} {'latency':8s}"
    print(header)

    for name in ["A", "B", "C", "D", "E", "F"]:
        r = run_config(name, dataset)
        note = "  (Pending Corpus)" if name in ("D", "E") else ""
        print(f"{name:30s} {str(r['retrieval_recall']):10s} {str(r['answer_keyword_recall']):9s} "
              f"{str(r['abstention_accuracy']):10s} {str(r['avg_citations']):7s} {str(r['latency_s']):8s}{note}")

    print("=" * 90)
    print("D(+Authority) / E(+Temporal) 因语料无权威/时间元数据，结果无意义，标记 Pending Corpus。")


if __name__ == "__main__":
    main()
