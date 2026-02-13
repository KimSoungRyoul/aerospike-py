.PHONY: dev backend frontend install build lint test docker-up docker-down

# Development
dev: backend frontend

backend:
	cd backend && uv run uvicorn main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

install:
	cd backend && uv sync
	cd frontend && npm install

# Quality
lint:
	cd backend && uv run ruff check .

test:
	cd backend && uv run pytest

# Build
build:
	cd frontend && npm run build

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down
