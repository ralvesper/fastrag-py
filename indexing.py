import json

from google import genai
from sqlalchemy.orm import Session

from config import settings
from models import Document
from schemas import DocumentIn

# .strip() remove \r do .env (Windows) — causa erro 400 na API do Gemini
client = genai.Client(api_key=settings.gemini_api_key.strip())


def embed_text(text: str) -> list[float]:
    """Converte texto em vetor de 1536 floats via Gemini."""
    result = client.models.embed_content(
        model=settings.embedding_model,
        contents=text,
    )
    return result.embeddings[0].values  # .values (não .embedding) — SDK mudou


def index_documents(db: Session, documents: list[DocumentIn]) -> int:
    """Indexa documentos manualmente (JSON direto). Para indexação em lote, ver doc_scanner.py."""
    for doc in documents:
        embedding = embed_text(doc.content)
        record = Document(
            content=doc.content,
            doc_type=doc.doc_type,
            metadata_json=json.dumps(doc.metadata) if doc.metadata else None,
            embedding_json=json.dumps(embedding),  # salva como string JSON (SQLite não tem tipo vetorial)
        )
        db.add(record)
    db.commit()
    return len(documents)
