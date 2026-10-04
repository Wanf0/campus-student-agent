"""Citation 评测指标（文档级近似；claim 级需人工标注，已明确标注）。"""

from dataclasses import dataclass, field


@dataclass
class QuestionAnalysis:
    id: str
    category: str
    answerable: str          # A / B / C / tool
    gold_docs: set = field(default_factory=set)
    cited_docs: set = field(default_factory=set)
    retrieved_docs: set = field(default_factory=set)
    key_claims_hit: int = 0
    key_claims_total: int = 0
    classification: str = ""

    @property
    def relevant_cited(self) -> set:
        return self.cited_docs & self.gold_docs

    @property
    def missed(self) -> set:
        return self.gold_docs - self.cited_docs


def classify(qa: QuestionAnalysis) -> str:
    """将逐题结果归入四类之一。"""
    if qa.answerable == "C":
        return "correct_abstention" if not qa.cited_docs else "hallucination_risk"
    if not qa.gold_docs:
        return "n/a"
    if not qa.retrieved_docs:
        return "retrieval_failure"
    if qa.relevant_cited and len(qa.relevant_cited) >= len(qa.gold_docs):
        return "good_compression" if len(qa.cited_docs) <= len(qa.gold_docs) else "good_with_extra"
    return "citation_incomplete"


def compute_metrics(analyses: list[QuestionAnalysis]) -> dict:
    """聚合 citation 四指标（文档级）。"""
    a_analyses = [a for a in analyses if a.gold_docs and a.answerable in ("A", "B")]

    # Precision / Recall（仅 A 类有 gold）
    prec_num = prec_den = rec_num = rec_den = 0
    for a in a_analyses:
        if a.cited_docs:
            prec_num += len(a.relevant_cited)
            prec_den += len(a.cited_docs)
        rec_num += len(a.relevant_cited)
        rec_den += len(a.gold_docs)

    # Completeness（key_claims 命中率，近似 claim 支持度）
    comp_num = sum(a.key_claims_hit for a in a_analyses)
    comp_den = sum(a.key_claims_total for a in a_analyses)

    return {
        "citation_precision": round(prec_num / prec_den, 3) if prec_den else None,
        "citation_recall": round(rec_num / rec_den, 3) if rec_den else None,
        "citation_completeness": round(comp_num / comp_den, 3) if comp_den else None,
        "citation_correctness": "doc-level: 与 precision 同源；claim 级需人工标注（Deferred）",
        "n_a_questions": len(a_analyses),
    }


def count_classifications(analyses: list[QuestionAnalysis]) -> dict:
    counts = {}
    for a in analyses:
        a.classification = classify(a)
        counts[a.classification] = counts.get(a.classification, 0) + 1
    return counts
