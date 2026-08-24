from fastapi import FastAPI

from database import init_db
from routes import router

# Entry point — roda com: uvicorn fastrag:app --reload --port 8000
app = FastAPI(title="Fastrag API", description="RAG API for document indexing, search and recommendations", version="1.0.0")

# Todas as rotas ficam sob /demo/ (ex: /demo/search, /demo/recommend)
app.include_router(router, prefix="/demo")


@app.get("/health")
def health():
    return {"status": "ok"}


# Cria tabelas automaticamente ao subir (SQLite ou PostgreSQL)
@app.on_event("startup")
def startup():
    init_db()
