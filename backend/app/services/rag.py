import chromadb

from ..config import settings

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
    res = col.query(query_embeddings=[query_embedding], n_results=n_results)
    return res
