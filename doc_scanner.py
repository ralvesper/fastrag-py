import hashlib
import json
import time
from pathlib import Path

from sqlalchemy.orm import Session

from indexing import embed_text
from models import Document
from schemas import DocumentIn


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


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
                    "hash": content_hash(content),
                },
            ))
    return docs


def _existing_by_path(db: Session) -> dict[tuple[str, str], Document]:
    existing: dict[tuple[str, str], Document] = {}
    for row in db.query(Document).all():
        meta = json.loads(row.metadata_json) if row.metadata_json else {}
        key = (meta.get("source", ""), meta.get("path", ""))
        if key != ("", ""):
            existing[key] = row
    return existing


def index_docs(db: Session, docs: list[DocumentIn]) -> tuple[int, int, int, dict[str, int]]:
    """Indexa apenas docs novos ou alterados. Retorna (novos, atualizados, pulados, sources)."""
    existing = _existing_by_path(db)
    indexed = updated = skipped = 0
    sources: dict[str, int] = {}
    pending = 0
    for doc in docs:
        meta = doc.metadata or {}
        key = (meta.get("source", ""), meta.get("path", ""))
        old = existing.get(key)
        if old is not None:
            old_hash = json.loads(old.metadata_json).get("hash") if old.metadata_json else None
            if old_hash == meta.get("hash"):
                skipped += 1
                continue
            db.delete(old)
            updated += 1
        else:
            indexed += 1

        src = meta.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1

        # rate limit: pausa a cada 3 embeddings pra não estourar cota da API
        if pending > 0 and pending % 3 == 0:
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
        pending += 1
        record = Document(
            content=doc.content,
            doc_type=doc.doc_type,
            metadata_json=json.dumps(meta),
            embedding_json=json.dumps(embedding),
        )
        db.add(record)
    db.commit()
    return indexed, updated, skipped, sources
