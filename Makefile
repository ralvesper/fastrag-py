.PHONY: run install build up down logs restart

# Local
run:
	uvicorn fastrag:app --reload --port 8000

install:
	pip install -r requirements.txt

# Docker
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f app

restart:
	docker compose restart app
