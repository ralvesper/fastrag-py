# Fastrag-py

RAG API para indexação e busca semântica de documentação.

## Pré-requisitos

- Python 3.12+
- Chave API Google Gemini
- Docker + Docker Compose (opcional, para PostgreSQL)
- sqlite3 CLI (opcional, para inspecionar banco local)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # editar com GEMINI_API_KEY
```

## Run

```bash
# Local (SQLite)
make run

# Docker (PostgreSQL + pgvector)
make up
```

## Makefile

| Comando | Função |
|---------|--------|
| `make run` | Roda local com SQLite |
| `make install` | Instala dependências |
| `make build` | Build da imagem Docker |
| `make up` | Sobe app + PostgreSQL |
| `make down` | Para containers |
| `make logs` | Logs do app |

## Uso

```bash
# Indexar docs
curl -X POST http://localhost:8000/demo/index-docs \
  -H "Content-Type: application/json" \
  -d '{"repo_paths": ["/caminho/para/docs"]}'

# Re-indexar (limpa antes)
curl -X POST http://localhost:8000/demo/index-docs \
  -H "Content-Type: application/json" \
  -d '{"repo_paths": ["/caminho/para/docs"], "reset": true}'

# Buscar
curl -X POST http://localhost:8000/demo/search \
  -H "Content-Type: application/json" \
  -d '{"query": "como cancelar pedido"}'

# Recomendar (RAG + LLM)
curl -X POST http://localhost:8000/demo/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "bug de creditDate"}'
```

## Acessar banco de dados

**PostgreSQL (Docker):**
| Campo | Valor |
|-------|-------|
| Host | `localhost` |
| Porta | `5432` |
| Database | `fastrag` |
| Usuário | `postgres` |
| Senha | `postgres` |

```bash
psql -h localhost -U postgres -d fastrag
# Senha: postgres
SELECT count(*) FROM documents;
\q
```

**SQLite (local):** não tem usuário/senha — arquivo direto.

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('fastrag.db')
c = conn.cursor()
c.execute('SELECT count(*) FROM documents')
print('Documentos:', c.fetchone()[0])
conn.close()
"
```
