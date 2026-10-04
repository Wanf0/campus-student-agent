"""逐题 citation 分析：对评测集逐题跑 agent，输出 retrieved/cited/missed 与分类。"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.domain.agent import CampusAgent
from app.domain.tools.knowledge_tool import search_knowledge
from citation_metrics import QuestionAnalysis, compute_metrics, count_classifications, classify

DATASET = Path(__file__).parent / "datasets" / "campus_qa.json"


def main():
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    agent = CampusAgent()
    analyses: list[QuestionAnalysis] = []

    print("=" * 100)
    print("逐题 citation 分析")
    print("=" * 100)
    header = f"{'id':16s} {'类别':10s} {'A/B/C':5s} {'gold':4s} {'retr':4s} {'cited':5s} {'rel':4s} {'missed':6s} 判定"
    print(header)

    for item in dataset:
        query = item["query"]
        gold = set(item.get("gold_documents", []))
        kws = item.get("expected_keywords", [])

        # retrieved = 检索后、相关性过滤前
        retrieved = {e.source_title for e in search_knowledge(query)}

        # cited = agent 最终引用（过滤后）
        out = agent.run(query)
        cited = {c.title for c in out.citations}

        hit = sum(1 for kw in kws if kw in out.answer)

        qa = QuestionAnalysis(
            id=item["id"],
            category=item["category"],
            answerable=item.get("answerable_from_corpus", "A"),
            gold_docs=gold,
            cited_docs=cited,
            retrieved_docs=retrieved,
            key_claims_hit=hit,
            key_claims_total=len(kws),
        )
        qa.classification = classify(qa)
        analyses.append(qa)

        rel = len(qa.relevant_cited)
        missed = len(qa.missed)
        print(f"{qa.id:16s} {qa.category:10s} {qa.answerable:5s} {len(gold):4d} "
              f"{len(retrieved):4d} {len(cited):5d} {rel:4d} {missed:6d}  {qa.classification}")

    print("=" * 100)
    metrics = compute_metrics(analyses)
    for k, v in metrics.items():
        print(f"{k}: {v}")

    print("-" * 100)
    print("分类统计:", count_classifications(analyses))


if __name__ == "__main__":
    main()
