"""重排序：使用交叉编码器对候选片段重排。"""

from sentence_transformers import CrossEncoder

from ..config import settings

_model = None
_failed = False


def _get_model():
    global _model, _failed
    if _model is None and not _failed:
        try:
            _model = CrossEncoder(settings.rerank_model)
        except Exception:
            _failed = True
    return _model


def rerank(query: str, candidates: list[dict]) -> list[dict]:
    """按相关性重排候选片段。若模型不可用则原样返回。"""
    model = _get_model()
    if model is None or not candidates:
        return candidates
    pairs = [(query, c["text"]) for c in candidates]
    try:
        scores = model.predict(pairs)
        for c, s in zip(candidates, scores):
            c["rerank_score"] = float(s)
        candidates.sort(key=lambda c: c.get("rerank_score", 0.0), reverse=True)
    except Exception:
        pass
    return candidates
