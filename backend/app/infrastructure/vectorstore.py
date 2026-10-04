import chromadb

from app.config import settings

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.chroma_dir)
        _collection = _client.get_or_create_collection(
            name="campus_knowledge",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict]):
    col = get_collection()
    col.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)


def query(query_embedding: list[float], n_results: int = 5) -> dict:
    col = get_collection()
    return col.query(query_embeddings=[query_embedding], n_results=n_results)


def delete_chunks(ids: list[str]):
    if not ids:
        return
    col = get_collection()
    col.delete(ids=ids)


def all_chunks() -> tuple[list[str], list[str], list[dict]]:
    """返回全部 (ids, documents, metadatas)，用于 BM25 索引与元数据索引构建。"""
    col = get_collection()
    data = col.get()
    return (
        data.get("ids") or [],
        data.get("documents") or [],
        data.get("metadatas") or [],
    )
