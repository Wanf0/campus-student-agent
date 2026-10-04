"""权威感知混合检索：向量 + BM25 → 时效过滤 → 权威加权 → RRF 融合 → Evidence。"""

import re
from datetime import datetime

from rank_bm25 import BM25Okapi

from app.config import settings
from app.domain.entities import Evidence
from app.infrastructure import embedding, vectorstore

_bm25 = None
_chunk_docs: list[str] = []
_chunk_metas: list[dict] = []
_chunk_ids: list[str] = []

_ASCII = re.compile(r"[a-zA-Z0-9]+")
_CHINESE = re.compile(r"[\u4e00-\u9fff]+")


def tokenize(text: str) -> list[str]:
    tokens = []
    tokens.extend(_ASCII.findall(text.lower()))
    for seg in _CHINESE.findall(text):
        tokens.extend(seg)
        tokens.extend(seg[i:i + 2] for i in range(len(seg) - 1))
    return tokens


def _ensure_bm25():
    global _bm25, _chunk_docs, _chunk_metas, _chunk_ids
    if _bm25 is not None:
        return
    _chunk_ids, _chunk_docs, _chunk_metas = vectorstore.all_chunks()
    _bm25 = BM25Okapi([tokenize(t) for t in _chunk_docs])


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _is_expired(meta: dict) -> bool:
    """effective_to 早于今天则视为过期。"""
    eff_to = meta.get("effective_to") or ""
    if not eff_to:
        return False
    try:
        return eff_to < _today()
    except Exception:
        return False


def _dedupe_latest(candidates: list[dict]) -> list[dict]:
    """同 title 保留版本最高者（版本字符串比较，缺失按 '0' 处理）。"""
    best: dict[str, dict] = {}
    for c in candidates:
        title = (c["meta"] or {}).get("title", "")
        ver = (c["meta"] or {}).get("version") or "0"
        if title not in best or ver >= (best[title]["meta"].get("version") or "0"):
            best[title] = c
    return list(best.values())


def _authority_weight(meta: dict) -> float:
    """权威等级加权系数：校级 1.3 / 院级 1.1 / 部门 1.0 / 未知 0.9。"""
    a = meta.get("source_authority", 1)
    return {4: 1.3, 3: 1.1, 2: 1.0, 1: 0.9}.get(a, 0.9)


def hybrid_search(query: str, top_k: int | None = None) -> list[Evidence]:
    """返回候选 Evidence 列表（已融合、过滤、加权）。"""
    top_k = top_k or settings.retrieval_top_k

    # 向量检索
    q_emb = embedding.embed_text(query)
    res = vectorstore.query(q_emb, n_results=top_k)
    vec_ids = (res.get("ids") or [[]])[0]
    vec_docs = (res.get("documents") or [[]])[0]
    vec_metas = (res.get("metadatas") or [[]])[0]

    # BM25 检索
    _ensure_bm25()
    bm25_scores = _bm25.get_scores(tokenize(query))
    ranked = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]

    # RRF 融合（含权威加权）
    rrf: dict[str, float] = {}
    info: dict[str, dict] = {}
    K = 60
    for rank, cid in enumerate(vec_ids):
        meta = vec_metas[rank] if vec_metas else {}
        w = _authority_weight(meta)
        rrf[cid] = rrf.get(cid, 0.0) + w / (K + rank + 1)
        info[cid] = {"text": vec_docs[rank], "meta": meta}
    for rank, idx in enumerate(ranked):
        cid = _chunk_ids[idx]
        meta = _chunk_metas[idx] if idx < len(_chunk_metas) else {}
        w = _authority_weight(meta)
        rrf[cid] = rrf.get(cid, 0.0) + w / (K + rank + 1)
        info.setdefault(cid, {"text": _chunk_docs[idx], "meta": meta})

    fused = sorted(rrf.items(), key=lambda x: x[1], reverse=True)

    # 时效过滤 + 版本归并
    candidates = []
    for cid, score in fused:
        meta = info[cid]["meta"]
        if _is_expired(meta):
            continue
        candidates.append({"text": info[cid]["text"], "meta": meta, "score": score})

    candidates = _dedupe_latest(candidates)[:top_k]

    return [
        Evidence(
            text=c["text"],
            source_title=c["meta"].get("title", ""),
            source_authority=c["meta"].get("source_authority", 1),
            publish_date=c["meta"].get("publish_date") or None,
            effective_from=c["meta"].get("effective_from") or None,
            effective_to=c["meta"].get("effective_to") or None,
            version=c["meta"].get("version") or None,
            department=c["meta"].get("department") or None,
            doc_type=c["meta"].get("doc_type", "其他"),
            retrieval_score=c["score"],
        )
        for c in candidates
    ]
