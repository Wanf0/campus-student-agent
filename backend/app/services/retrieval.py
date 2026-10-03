"""混合检索：向量检索 + BM25 关键词检索，通过 RRF 融合。"""

import re

from rank_bm25 import BM25Okapi

from . import rag, embedding

_bm25 = None
_chunk_texts: list[str] = []
_chunk_ids: list[str] = []

_ASCII = re.compile(r"[a-zA-Z0-9]+")
_CHINESE = re.compile(r"[\u4e00-\u9fff]+")


def tokenize(text: str) -> list[str]:
    """中文按字 + 二元组切分，英文/数字按词切分。"""
    tokens = []
    tokens.extend(_ASCII.findall(text.lower()))
    for seg in _CHINESE.findall(text):
        tokens.extend(seg)  # 单字
        tokens.extend(seg[i:i + 2] for i in range(len(seg) - 1))  # 二元组
    return tokens


def _ensure_bm25():
    global _bm25, _chunk_texts, _chunk_ids
    if _bm25 is not None:
        return
    data = rag.get_collection().get()
    _chunk_texts = data.get("documents") or []
    _chunk_ids = data.get("ids") or []
    _bm25 = BM25Okapi([tokenize(t) for t in _chunk_texts])


def hybrid_search(query: str, top_k: int = 8) -> list[dict]:
    """返回融合后的候选片段列表 [{text, meta, score}]。"""
    # 向量检索
    q_emb = embedding.embed_text(query)
    res = rag.query(q_emb, n_results=top_k)
    vec_ids = (res.get("ids") or [[]])[0]
    vec_docs = (res.get("documents") or [[]])[0]
    vec_metas = (res.get("metadatas") or [[]])[0]

    # BM25 检索
    _ensure_bm25()
    bm25_scores = _bm25.get_scores(tokenize(query))
    ranked = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]

    # RRF 融合
    rrf: dict[str, float] = {}
    info: dict[str, dict] = {}
    K = 60
    for rank, cid in enumerate(vec_ids):
        rrf[cid] = rrf.get(cid, 0.0) + 1.0 / (K + rank + 1)
        info[cid] = {"text": vec_docs[rank], "meta": vec_metas[rank] if vec_metas else {}}
    for rank, idx in enumerate(ranked):
        cid = _chunk_ids[idx]
        rrf[cid] = rrf.get(cid, 0.0) + 1.0 / (K + rank + 1)
        info.setdefault(cid, {"text": _chunk_texts[idx], "meta": {}})

    fused = sorted(rrf.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{"text": info[cid]["text"], "meta": info[cid]["meta"], "score": score} for cid, score in fused]
