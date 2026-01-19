.PHONY: help setup install install-backend install-frontend run run-backend run-frontend test test-backend test-frontend lint lint-backend lint-frontend format format-backend format-frontend clean clean-backend clean-frontend migrate list-users reset-password activate-user

help:
	@echo "Available commands:"
	@echo "  make setup            - Setup .env file from .env.example"
	@echo "  make install          - Install all dependencies (backend + frontend)"
	@echo "  make run              - Run both backend and frontend servers"
	@echo "  make test             - Run all tests"
	@echo "  make lint             - Run all linters"
	@echo "  make format           - Format all code"
	@echo "  make clean            - Clean all build artifacts"
	@echo "  make migrate          - Run database migrations"
	@echo ""
	@echo "Backend-specific:"
	@echo "  make install-backend  - Install backend dependencies"
	@echo "  make run-backend      - Run backend server"
	@echo "  make test-backend     - Run backend tests"
	@echo "  make lint-backend     - Lint backend code"
	@echo "  make format-backend   - Format backend code"
	@echo ""
	@echo "Frontend-specific:"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo "  make run-frontend     - Run frontend dev server"
	@echo "  make test-frontend    - Run frontend tests"
	@echo "  make lint-frontend    - Lint frontend code"
	@echo "  make format-frontend  - Format frontend code"
	@echo ""
	@echo "User management:"
	@echo "  make list-users                    - List all users"
	@echo "  make reset-password EMAIL=<email> - Reset password and activate user"
	@echo "  make activate-user EMAIL=<email>  - Activate a user account"

# Setup
setup:
	@echo "🔧 Setting up environment..."
	@if command -v python3 > /dev/null 2>&1; then \
		python3 scripts/setup-env.py; \
	else \
		bash scripts/setup-env.sh; \
	fi

# Installation
install: install-backend install-frontend
	@echo "✅ All dependencies installed"

install-backend:
	@echo "📦 Installing backend dependencies..."
	cd backend && poetry install

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

# Run servers
run:
	@echo "🚀 Starting servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "API Docs: http://localhost:8000/docs"
	@$(MAKE) -j 2 run-backend run-frontend

run-backend:
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

# Testing
test: test-backend test-frontend
	@echo "✅ All tests completed"

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && poetry run pytest -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm run test

# Linting
lint: lint-backend lint-frontend
	@echo "✅ Linting completed"

lint-backend:
	@echo "🔍 Linting backend..."
	cd backend && poetry run ruff check .
	cd backend && poetry run mypy app

lint-frontend:
	@echo "🔍 Linting frontend..."
	cd frontend && npm run lint

# Formatting
format: format-backend format-frontend
	@echo "✅ Formatting completed"

format-backend:
	@echo "🎨 Formatting backend..."
	cd backend && poetry run black .
	cd backend && poetry run ruff check --fix .

format-frontend:
	@echo "🎨 Formatting frontend..."
	cd frontend && npm run format

# Database migrations
migrate:
	@echo "🗄️  Running database migrations..."
	cd backend && poetry run alembic upgrade head

migrate-create:
	@echo "🗄️  Creating new migration..."
	@read -p "Enter migration message: " message; \
	cd backend && poetry run alembic revision --autogenerate -m "$$message"

# Cleanup
clean: clean-backend clean-frontend
	@echo "✅ Cleanup completed"

clean-backend:
	@echo "🧹 Cleaning backend..."
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true
	find backend -type f -name "*.pyo" -delete 2>/dev/null || true
	find backend -type f -name "*.db" -delete 2>/dev/null || true
	rm -rf backend/.coverage backend/htmlcov 2>/dev/null || true

clean-frontend:
	@echo "🧹 Cleaning frontend..."
	rm -rf frontend/node_modules frontend/dist frontend/.cache 2>/dev/null || true
	find frontend -type f -name "*.log" -delete 2>/dev/null || true

# Development helpers
dev-setup: setup install migrate
	@echo "✅ Development environment ready"
	@echo "Run 'make run' to start servers"

first-time-setup: setup install migrate
	@echo "✅ First-time setup complete!"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "   make run       - Start both servers"
	@echo "   make test      - Run all tests"
	@echo ""
	@echo "📚 Documentation:"
	@echo "   Backend:  http://localhost:8000/docs"
	@echo "   Frontend: http://localhost:5173"

backend-shell:
	cd backend && poetry shell

db-reset:
	@echo "⚠️  Resetting database..."
	rm -f backend/app.db backend/app.db-journal
	$(MAKE) migrate
	@echo "✅ Database reset complete"

# User management
list-users:
	@echo "📋 Listing users..."
	cd backend && poetry run python -m app.scripts.reset_password --list

reset-password:
	@echo "🔐 Password reset utility"
	@echo "Usage: make reset-password EMAIL=user@example.com"
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL is required"; \
		echo "Example: make reset-password EMAIL=admin@example.com"; \
		exit 1; \
	fi
	cd backend && poetry run python -m app.scripts.reset_password --email $(EMAIL) --generate --activate

activate-user:
	@echo "👤 Activating user..."
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL is required"; \
		echo "Example: make activate-user EMAIL=user@example.com"; \
		exit 1; \
	fi
	cd backend && poetry run python -m app.scripts.reset_password --email $(EMAIL) --activate-only


