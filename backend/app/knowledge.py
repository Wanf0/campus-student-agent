"""知识库文档导入：清洗 → 切分 → 向量化 → 存入 Chroma 与 MySQL。"""

import re

from sqlalchemy.orm import Session

from .models import Document, Chunk
from .services import embedding, rag

_SENT_SPLIT = re.compile(r"(?<=[。！？!?；;\n])")


def split_text(text: str, chunk_size: int = 300, overlap: int = 60) -> list[str]:
    """按句切分后，聚合成带重叠的文本块。"""
    sentences = [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]
    chunks: list[str] = []
    current = ""
    for s in sentences:
        if len(current) + len(s) <= chunk_size:
            current += s
        else:
            if current:
                chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    return chunks


def ingest_document(db: Session, title: str, category: str, source: str | None, content: str) -> int:
    """导入一篇文档，返回文档 id。"""
    doc = Document(title=title, category=category, source=source, content=content)
    db.add(doc)
    db.flush()  # 获取 doc.id

    texts = split_text(content)
    chunk_ids: list[str] = []
    metadatas: list[dict] = []
    for text in texts:
        chunk = Chunk(document_id=doc.id, content=text, embedding_id="")
        db.add(chunk)
        db.flush()
        chunk.embedding_id = f"chunk_{chunk.id}"
        chunk_ids.append(chunk.embedding_id)
        metadatas.append({"title": title, "category": category})

    db.commit()

    if texts:
        vectors = embedding.embed_texts(texts)
        rag.add_chunks(
            ids=chunk_ids,
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas,
        )
    return doc.id
