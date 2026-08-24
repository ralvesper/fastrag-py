import json
import time
from pathlib import Path

from sqlalchemy.orm import Session

from indexing import embed_text
from models import Document
from schemas import DocumentIn


def scan_docs(repo_paths: list[str]) -> list[DocumentIn]:
    docs = []
    for repo_path in repo_paths:
        repo = Path(repo_path)
        if not repo.exists():
            continue
        source = repo.name
        for md in repo.rglob("*.md"):
            if ".git" in md.parts or ".venv" in md.parts:
                continue
            content = md.read_text(encoding="utf-8", errors="ignore").strip()
            if not content:
                continue
            rel = md.relative_to(repo)
            docs.append(DocumentIn(
                content=content,
                doc_type="documentation",
                metadata={
                    "source": source,
                    "path": str(rel),
                    "filename": md.name,
                },
            ))
    return docs


def index_docs(db: Session, docs: list[DocumentIn]) -> int:
    for i, doc in enumerate(docs):
        if i > 0 and i % 3 == 0:
            time.sleep(3)
        for attempt in range(5):
            try:
                embedding = embed_text(doc.content)
                break
            except Exception as e:
                if "429" in str(e) and attempt < 4:
                    wait = 10 * (attempt + 1)
                    time.sleep(wait)
                else:
                    raise
        record = Document(
            content=doc.content,
            doc_type=doc.doc_type,
            metadata_json=json.dumps(doc.metadata),
            embedding_json=json.dumps(embedding),
        )
        db.add(record)
    db.commit()
    return len(docs)
