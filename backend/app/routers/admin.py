from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..knowledge import ingest_document
from ..models import Document, Chunk
from ..schemas import DocumentCreate, DocumentResponse
from ..services import rag

router = APIRouter(prefix="/admin", tags=["管理"])


@router.post("/documents", response_model=DocumentResponse)
def create_document(req: DocumentCreate, db: Session = Depends(get_db)):
    doc_id = ingest_document(db, req.title, req.category, req.source, req.content)
    return DocumentResponse(id=doc_id, title=req.title, category=req.category, source=req.source)


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return [DocumentResponse(id=d.id, title=d.title, category=d.category, source=d.source) for d in docs]


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    chunks = db.query(Chunk).filter(Chunk.document_id == doc_id).all()
    embedding_ids = [c.embedding_id for c in chunks if c.embedding_id]
    if embedding_ids:
        rag.delete_chunks(embedding_ids)
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id, "chunks_removed": len(embedding_ids)}
