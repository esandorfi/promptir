.PHONY: help install dev test lint format typecheck check clean

help:
	@echo "promptir UI Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install    Install all dependencies"
	@echo "  make dev        Start development servers"
	@echo ""
	@echo "Quality:"
	@echo "  make lint       Run linters"
	@echo "  make format     Format code"
	@echo "  make typecheck  Run type checkers"
	@echo "  make test       Run all tests"
	@echo "  make check      Run all checks (lint + type + test)"
	@echo ""
	@echo "Build:"
	@echo "  make build      Build for production"
	@echo "  make clean      Clean build artifacts"

# Setup
install:
	pip install -e ".[dev]"
	cd frontend && npm install

# Development
dev:
	@echo "Starting backend on http://localhost:8000"
	@echo "Starting frontend on http://localhost:5173"
	@(trap 'kill 0' SIGINT; \
		uvicorn backend.server:app --reload --port 8000 & \
		cd frontend && npm run dev & \
		wait)

# Backend commands
lint-backend:
	ruff check backend/
	ruff format --check backend/

format-backend:
	ruff format backend/
	ruff check --fix backend/

typecheck-backend:
	pyright backend/

test-backend:
	pytest backend/tests/ -v

# Frontend commands
lint-frontend:
	cd frontend && npm run lint

format-frontend:
	cd frontend && npm run format

typecheck-frontend:
	cd frontend && npm run typecheck

test-frontend:
	cd frontend && npm run test

# Combined commands
lint: lint-backend lint-frontend

format: format-backend format-frontend

typecheck: typecheck-backend typecheck-frontend

test: test-backend test-frontend

check: lint typecheck test

# Build
build:
	cd frontend && npm run build

clean:
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	rm -rf backend/__pycache__
	rm -rf backend/tests/__pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
