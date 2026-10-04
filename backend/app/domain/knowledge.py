"""知识库文档导入：清洗 → 切分 → 向量化 → 存入 Chroma 与 DB（含时效/权威元数据）。"""

import re

from sqlalchemy.orm import Session

from app.domain.models import Document, Chunk
from app.infrastructure import embedding, vectorstore

_SENT_SPLIT = re.compile(r"(?<=[。！？!?；;\n])")


def split_text(text: str, chunk_size: int = 300, overlap: int = 60) -> list[str]:
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


def ingest_document(
    db: Session,
    title: str,
    category: str,
    source: str | None,
    content: str,
    source_authority: int = 1,
    publish_date: str | None = None,
    effective_from: str | None = None,
    effective_to: str | None = None,
    version: str | None = None,
    department: str | None = None,
    doc_type: str = "其他",
) -> int:
    doc = Document(
        title=title,
        category=category,
        source=source,
        content=content,
        source_authority=source_authority,
        publish_date=publish_date,
        effective_from=effective_from,
        effective_to=effective_to,
        version=version,
        department=department,
        doc_type=doc_type,
    )
    db.add(doc)
    db.flush()

    texts = split_text(content)
    chunk_ids: list[str] = []
    metadatas: list[dict] = []
    for text in texts:
        chunk = Chunk(document_id=doc.id, content=text, embedding_id="")
        db.add(chunk)
        db.flush()
        chunk.embedding_id = f"chunk_{chunk.id}"
        chunk_ids.append(chunk.embedding_id)
        metadatas.append({
            "title": title,
            "category": category,
            "source_authority": source_authority,
            "publish_date": publish_date or "",
            "effective_from": effective_from or "",
            "effective_to": effective_to or "",
            "version": version or "",
            "department": department or "",
            "doc_type": doc_type,
        })

    db.commit()

    if texts:
        vectors = embedding.embed_texts(texts)
        vectorstore.add_chunks(ids=chunk_ids, documents=texts, embeddings=vectors, metadatas=metadatas)
    return doc.id
