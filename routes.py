from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from indexing import index_documents
from retrieval import search
from generation import recommend
from doc_scanner import scan_docs, index_docs
from schemas import (
    IndexRequest,
    IndexResponse,
    IndexDocsRequest,
    IndexDocsResponse,
    SearchRequest,
    SearchResponse,
    RecommendRequest,
    RecommendResponse,
)

router = APIRouter()


@router.post("/index", response_model=IndexResponse)
def index(req: IndexRequest, db: Session = Depends(get_db)):
    count = index_documents(db, req.documents)
    return IndexResponse(indexed=count)


@router.post("/index-docs", response_model=IndexDocsResponse)
def index_docs_endpoint(req: IndexDocsRequest, db: Session = Depends(get_db)):
    if req.reset:
        db.execute(text("DELETE FROM documents"))
        db.commit()
    docs = scan_docs(req.repo_paths)
    indexed, updated, skipped, sources = index_docs(db, docs)
    return IndexDocsResponse(indexed=indexed, updated=updated, skipped=skipped, sources=sources)


@router.post("/search", response_model=SearchResponse)
def search_documents(req: SearchRequest, db: Session = Depends(get_db)):
    results = search(db, req.query, req.doc_type, req.top_k, req.source)
    return SearchResponse(results=results)


@router.post("/recommend", response_model=RecommendResponse)
def recommend_documents(req: RecommendRequest):
    answer, sources = recommend(req.query, req.doc_type, req.top_k, req.source)
    return RecommendResponse(answer=answer, sources=sources)
