.PHONY: help install dev test lint format typecheck check clean build docker-build docker-run pre-commit-install pre-commit

help:
	@echo "promptir UI Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install           Install all dependencies (requires uv and npm)"
	@echo "  make pre-commit-install Install pre-commit hooks"
	@echo "  make dev               Start development servers"
	@echo ""
	@echo "Quality:"
	@echo "  make lint              Run linters"
	@echo "  make format            Format code"
	@echo "  make typecheck         Run type checkers"
	@echo "  make test              Run all tests"
	@echo "  make check             Run all checks (lint + type + test)"
	@echo "  make pre-commit        Run pre-commit on all files"
	@echo ""
	@echo "Build:"
	@echo "  make build             Build frontend for production"
	@echo "  make clean             Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      Build Docker image"
	@echo "  make docker-run        Run Docker container"

# Setup
install:
	uv sync --dev
	cd frontend && npm install
	@echo ""
	@echo "Run 'make pre-commit-install' to enable pre-commit hooks"

# Pre-commit hooks
pre-commit-install:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run --all-files

# Development
dev:
	@echo "Starting backend on http://localhost:8000"
	@echo "Starting frontend on http://localhost:5173"
	@(trap 'kill 0' SIGINT; \
		uv run uvicorn backend.server:app --reload --port 8000 & \
		cd frontend && npm run dev & \
		wait)

# Backend only
dev-backend:
	uv run uvicorn backend.server:app --reload --port 8000

# Frontend only
dev-frontend:
	cd frontend && npm run dev

# Backend commands
lint-backend:
	uv run ruff check backend/
	uv run ruff format --check backend/

format-backend:
	uv run ruff format backend/
	uv run ruff check --fix backend/

typecheck-backend:
	uv run pyright backend/

test-backend:
	uv run pytest backend/tests/ -v

test-backend-cov:
	uv run pytest backend/tests/ -v --cov=backend --cov-report=term-missing

# Frontend commands
lint-frontend:
	cd frontend && npm run lint

format-frontend:
	cd frontend && npm run format

typecheck-frontend:
	cd frontend && npm run typecheck

test-frontend:
	cd frontend && npm run test

test-frontend-cov:
	cd frontend && npm run test:coverage

# Combined commands
lint: lint-backend lint-frontend

format: format-backend format-frontend

typecheck: typecheck-backend typecheck-frontend

test: test-backend test-frontend

check: lint typecheck test

# Build
build:
	cd frontend && npm run build

# Clean
clean:
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	rm -rf backend/__pycache__
	rm -rf backend/tests/__pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .venv

# Docker
docker-build:
	docker build -t promptir-ui .

docker-run:
	docker run -p 8000:8000 \
		-e OPENAI_API_KEY=$${OPENAI_API_KEY} \
		-v $$(pwd)/../data:/app/data:ro \
		promptir-ui
