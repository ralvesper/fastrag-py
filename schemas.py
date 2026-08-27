from pydantic import BaseModel


class DocumentIn(BaseModel):
    content: str
    doc_type: str = "generic"
    metadata: dict | None = None


class DocumentOut(BaseModel):
    id: int
    content: str
    doc_type: str
    metadata: dict | None = None


class IndexRequest(BaseModel):
    documents: list[DocumentIn]


class IndexResponse(BaseModel):
    indexed: int


class IndexDocsRequest(BaseModel):
    repo_paths: list[str]
    reset: bool = False  # se true, apaga todos os documentos antes de indexar


class IndexDocsResponse(BaseModel):
    indexed: int
    updated: int = 0
    skipped: int = 0
    sources: dict[str, int]


class SearchRequest(BaseModel):
    query: str
    doc_type: str | None = None
    source: str | None = None
    top_k: int = 4


class SearchResult(BaseModel):
    id: int
    content: str
    doc_type: str
    metadata: dict | None = None
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]


class RecommendRequest(BaseModel):
    query: str
    doc_type: str | None = None
    source: str | None = None
    top_k: int = 4


class RecommendResponse(BaseModel):
    answer: str
    sources: list[SearchResult]
