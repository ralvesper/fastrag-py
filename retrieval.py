import json

import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

from indexing import embed_text
from schemas import SearchResult


def search(
    db: Session,
    query: str,
    doc_type: str | None = None,
    top_k: int = 4,
    source: str | None = None,
) -> list[SearchResult]:
    """Busca vetorial por cosine similarity. Filtros: doc_type, source."""
    query_embedding = np.array(embed_text(query), dtype=np.float32)

    # Monta WHERE dinâmico com parâmetros seguros (evita SQL injection)
    where_clauses = []
    params: dict = {}
    if doc_type:
        where_clauses.append("doc_type = :doc_type")
        params["doc_type"] = doc_type
    if source:
        # json_extract: extrai campo do JSON salvo no SQLite
        where_clauses.append("json_extract(metadata_json, '$.source') = :source")
        params["source"] = source

    where = ""
    if where_clauses:
        where = "WHERE " + " AND ".join(where_clauses)

    sql = text(f"SELECT id, content, doc_type, metadata_json, embedding_json FROM documents {where}")
    rows = db.execute(sql, params).fetchall()

    # Calcula cosine similarity para cada documento
    scored = []
    for row in rows:
        emb = np.array(json.loads(row.embedding_json), dtype=np.float32)
        score = float(np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb)))
        scored.append(SearchResult(
            id=row.id,
            content=row.content,
            doc_type=row.doc_type,
            metadata=json.loads(row.metadata_json) if row.metadata_json else None,
            score=score,
        ))

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:top_k]
