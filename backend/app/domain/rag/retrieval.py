"""权威感知混合检索：向量 + BM25 → 时效过滤 → 权威加权 → RRF 融合 → Evidence。

支持通过 RetrievalConfig 控制各组件开关，用于 ablation。
"""

import re
from dataclasses import dataclass
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


@dataclass
class RetrievalConfig:
    """检索组件开关（用于 ablation）。"""
    use_bm25: bool = True
    use_authority: bool = True
    use_temporal: bool = True


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
    eff_to = meta.get("effective_to") or ""
    if not eff_to:
        return False
    try:
        return eff_to < _today()
    except Exception:
        return False


def _dedupe_latest(candidates: list[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for c in candidates:
        title = (c["meta"] or {}).get("title", "")
        ver = (c["meta"] or {}).get("version") or "0"
        if title not in best or ver >= (best[title]["meta"].get("version") or "0"):
            best[title] = c
    return list(best.values())


def _authority_weight(meta: dict) -> float:
    a = meta.get("source_authority", 1)
    return {4: 1.3, 3: 1.1, 2: 1.0, 1: 0.9}.get(a, 0.9)


def vector_search(query: str, top_k: int) -> list[Evidence]:
    """纯向量检索（naive 基线）。"""
    q_emb = embedding.embed_text(query)
    res = vectorstore.query(q_emb, n_results=top_k)
    ids = (res.get("ids") or [[]])[0]
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    out = []
    for i, cid in enumerate(ids):
        meta = metas[i] if metas else {}
        out.append(Evidence(
            text=docs[i],
            source_title=meta.get("title", ""),
            source_authority=meta.get("source_authority", 1),
            publish_date=meta.get("publish_date") or None,
            effective_from=meta.get("effective_from") or None,
            effective_to=meta.get("effective_to") or None,
            version=meta.get("version") or None,
            department=meta.get("department") or None,
            doc_type=meta.get("doc_type", "其他"),
        ))
    return out


def hybrid_search(query: str, top_k: int | None = None, config: RetrievalConfig | None = None) -> list[Evidence]:
    top_k = top_k or settings.retrieval_top_k
    cfg = config or RetrievalConfig()

    q_emb = embedding.embed_text(query)
    res = vectorstore.query(q_emb, n_results=top_k)
    vec_ids = (res.get("ids") or [[]])[0]
    vec_docs = (res.get("documents") or [[]])[0]
    vec_metas = (res.get("metadatas") or [[]])[0]

    rrf: dict[str, float] = {}
    info: dict[str, dict] = {}
    K = 60

    for rank, cid in enumerate(vec_ids):
        meta = vec_metas[rank] if vec_metas else {}
        w = _authority_weight(meta) if cfg.use_authority else 1.0
        rrf[cid] = rrf.get(cid, 0.0) + w / (K + rank + 1)
        info[cid] = {"text": vec_docs[rank], "meta": meta}

    if cfg.use_bm25:
        _ensure_bm25()
        bm25_scores = _bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
        for rank, idx in enumerate(ranked):
            cid = _chunk_ids[idx]
            meta = _chunk_metas[idx] if idx < len(_chunk_metas) else {}
            w = _authority_weight(meta) if cfg.use_authority else 1.0
            rrf[cid] = rrf.get(cid, 0.0) + w / (K + rank + 1)
            info.setdefault(cid, {"text": _chunk_docs[idx], "meta": meta})

    fused = sorted(rrf.items(), key=lambda x: x[1], reverse=True)

    candidates = []
    for cid, score in fused:
        meta = info[cid]["meta"]
        if cfg.use_temporal and _is_expired(meta):
            continue
        candidates.append({"text": info[cid]["text"], "meta": meta, "score": score})

    if cfg.use_temporal:
        candidates = _dedupe_latest(candidates)

    candidates = candidates[:top_k]

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
