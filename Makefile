.PHONY: run install build up down logs restart

# Local
install:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

run:
	.venv/bin/uvicorn fastrag:app --reload --port 8000

# Docker
build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f app

# Recria o container pra pegar mudanças no .env (restart não recarrega env)
restart:
	docker compose up -d --force-recreate app
