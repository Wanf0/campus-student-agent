"""Grounding：重排 + 引用 + 证据一致性上下文构建。"""

from app.config import settings
from app.domain.entities import Evidence, Citation
from app.infrastructure import rerank as rerank_infra


def rerank_evidence(query: str, evidence: list[Evidence]) -> list[Evidence]:
    """用交叉编码器对候选证据重排。"""
    if not evidence:
        return evidence
    candidates = [{"text": e.text, "meta": {}} for e in evidence]
    ranked = rerank_infra.rerank(query, candidates)
    score_map = {e.text: e for e in evidence}
    out = []
    for c in ranked:
        e = score_map.get(c["text"])
        if e is not None:
            e.rerank_score = c.get("rerank_score")
            out.append(e)
    return out


def to_citations(evidence: list[Evidence]) -> list[Citation]:
    return [
        Citation(title=e.source_title, authority=e.authority_label, publish_date=e.publish_date)
        for e in evidence
    ]


def build_grounded_context(evidence: list[Evidence]) -> str:
    """将证据组装为带来源/时间/权威标注的上下文。"""
    parts = []
    for e in evidence:
        meta = f"来源：{e.source_title}（{e.authority_label}"
        if e.publish_date:
            meta += f"，发布 {e.publish_date}"
        if e.effective_to:
            meta += f"，有效期至 {e.effective_to}"
        if e.version:
            meta += f"，版本 {e.version}"
        meta += "）"
        parts.append(f"{meta}\n{e.text}")
    return "\n\n---\n\n".join(parts)


def top_k_evidence(evidence: list[Evidence], k: int | None = None) -> list[Evidence]:
    k = k or settings.final_top_k
    return evidence[:k]
