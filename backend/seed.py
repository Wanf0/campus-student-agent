"""种子脚本：将 knowledge/ 目录下的 .txt 与 .pdf 文件导入知识库。

用法：在 backend 目录下执行
    .venv/bin/python seed.py
"""

from pathlib import Path

from pypdf import PdfReader

from app.db import Base, engine, SessionLocal
from app.knowledge import ingest_document

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    files = sorted(list(KNOWLEDGE_DIR.glob("*.txt")) + list(KNOWLEDGE_DIR.glob("*.pdf")))
    if not files:
        print("knowledge/ 目录下没有可导入的文件（.txt / .pdf）")
        return
    for f in files:
        title = f.stem
        try:
            content = read_pdf(f) if f.suffix.lower() == ".pdf" else f.read_text(encoding="utf-8")
        except Exception as e:
            print(f"跳过（解析失败）：{f.name}（{e}）")
            continue
        if not content.strip():
            print(f"跳过（无文字内容，可能是扫描件）：{f.name}")
            continue
        doc_id = ingest_document(db, title, "校园资料", str(f), content)
        print(f"已导入：{title}（文档 id={doc_id}）")
    db.close()


if __name__ == "__main__":
    main()
