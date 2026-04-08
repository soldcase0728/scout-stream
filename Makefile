.PHONY: setup db backend worker frontend dev test seed clean

# Full setup: install all dependencies
setup:
	@echo "==> Copying .env.example to .env (if not exists)..."
	@test -f .env || cp .env.example .env
	@echo "==> Installing backend dependencies..."
	cd backend && pip install -e ".[dev]"
	@echo "==> Installing frontend dependencies..."
	cd frontend && npm install
	@echo "==> Setup complete!"
	@echo "    Next: make db   (start PostgreSQL + Redis and run migrations)"

# Start infrastructure and run migrations
db:
	@echo "==> Starting PostgreSQL and Redis..."
	docker compose up -d
	@echo "==> Waiting for PostgreSQL to be ready..."
	@sleep 3
	@echo "==> Running database migrations..."
	cd backend && alembic upgrade head
	@echo "==> Database ready!"

# Start backend API server
backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker for video processing
worker:
	cd backend && celery -A processing.worker worker --loglevel=info

# Start frontend dev server
frontend:
	cd frontend && npm run dev

# Run all services (use separate terminals or background)
dev:
	@echo "Scout Stream Development"
	@echo "========================"
	@echo "Run these commands in separate terminal windows:"
	@echo ""
	@echo "  Terminal 1:  make db        # Start PostgreSQL + Redis"
	@echo "  Terminal 2:  make backend   # Start API at localhost:8000"
	@echo "  Terminal 3:  make worker    # Start video processing worker"
	@echo "  Terminal 4:  make frontend  # Start UI at localhost:3001"
	@echo ""
	@echo "Then: make seed              # Create test account"
	@echo "Then: open http://localhost:3001"

# Run backend tests
test:
	cd backend && pytest -v

# Seed test data (coach account + sample athlete)
seed:
	cd backend && python -m scripts.seed_data

# Stop infrastructure
stop:
	docker compose down

# Clean up generated files
clean:
	docker compose down -v
	rm -rf backend/uploads backend/processed
	rm -rf frontend/.next frontend/node_modules
