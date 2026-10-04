from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.api.schemas import DocumentCreate, DocumentResponse
from app.domain.knowledge import ingest_document
from app.domain.models import Document, Chunk
from app.infrastructure import vectorstore
from app.infrastructure.db import get_db

router = APIRouter(prefix="/admin", tags=["管理"])


def _extract_upload(filename: str, data: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    if filename.lower().endswith(".txt"):
        return data.decode("utf-8", errors="ignore").strip()
    raise HTTPException(status_code=400, detail="仅支持 .txt / .pdf 文件")


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = await file.read()
    text = _extract_upload(file.filename or "", data)
    if not text:
        raise HTTPException(status_code=400, detail="文件无文字内容（可能是扫描件）")
    title = (file.filename or "未命名").rsplit(".", 1)[0]
    doc_id = ingest_document(db, title, "校园资料", file.filename, text)
    return {"id": doc_id, "title": title}


@router.post("/documents", response_model=DocumentResponse)
def create_document(req: DocumentCreate, db: Session = Depends(get_db)):
    doc_id = ingest_document(
        db, req.title, req.category, req.source, req.content,
        source_authority=req.source_authority,
        publish_date=req.publish_date,
        effective_from=req.effective_from,
        effective_to=req.effective_to,
        version=req.version,
        department=req.department,
        doc_type=req.doc_type,
    )
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
        vectorstore.delete_chunks(embedding_ids)
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id, "chunks_removed": len(embedding_ids)}
