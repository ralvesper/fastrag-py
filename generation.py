from google import genai

from config import settings
from retrieval import search
from schemas import SearchResult
from database import SessionLocal

client = genai.Client(api_key=settings.gemini_api_key.strip())

SYSTEM_PROMPT = """Voce e um assistente de recomendacao. Responda com base no contexto recuperado.
Se nao houver informacao suficiente, diga que nao possui dados suficientes para responder."""


def recommend(
    query: str,
    doc_type: str | None = None,
    top_k: int = 4,
    source: str | None = None,
) -> tuple[str, list[SearchResult]]:
    """Pipeline RAG: busca documentos + monta prompt + gera resposta com LLM."""
    db = SessionLocal()
    try:
        sources = search(db, query, doc_type, top_k, source)
    finally:
        db.close()

    # Contexto: source/path + 500 chars por doc (evita estourar janela do LLM)
    context = "\n\n".join(
        f"[{i+1}] ({s.metadata.get('source', '?')}/{s.metadata.get('path', '?')}) {s.content[:500]}"
        for i, s in enumerate(sources)
    ) or "Nenhum documento encontrado."

    prompt = f"""{SYSTEM_PROMPT}

CONTEXTO RECUPERADO:
{context}

PERGUNTA:
{query}"""

    response = client.models.generate_content(
        model=settings.chat_model,
        contents=prompt,
    )

    return response.text, sources
