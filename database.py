from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings

# check_same_thread=False: necessário para SQLite em FastAPI (multi-thread)
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass  # marker — diz ao SQLAlchemy "essa classe representa uma tabela"


def init_db():
    # PostgreSQL: garante extensão pgvector para busca vetorial
    if "sqlite" not in settings.database_url:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    # Cria tabelas definidas nos models (idempotente)
    Base.metadata.create_all(bind=engine)


def get_db():
    # Generator — FastAPI usa como Dependency Injection
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
