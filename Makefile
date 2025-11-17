.PHONY: help setup start stop logs clean test

help:
	@echo "🚀 Aegra + Agent Chat UI Management"
	@echo "===================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  make setup          - Set up both Aegra and Agent Chat UI"
	@echo "  make start          - Start both services locally (no Docker)"
	@echo "  make start-docker   - Start all services with Docker Compose"
	@echo "  make stop           - Stop all services"
	@echo "  make stop-docker    - Stop Docker services"
	@echo "  make logs           - Show logs from running services"
	@echo "  make logs-docker    - Show Docker logs"
	@echo "  make clean          - Clean up all caches and data"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run integration tests"
	@echo "  make test-backend   - Test Aegra backend only"
	@echo "  make test-frontend  - Test Agent Chat UI only"
	@echo ""
	@echo "Database:"
	@echo "  make db-up          - Start PostgreSQL"
	@echo "  make db-down        - Stop PostgreSQL"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-reset       - Reset database (destructive)"
	@echo ""

setup:
	@echo "📦 Setting up Aegra..."
	@cd aegra && uv install
	@echo "✅ Aegra dependencies installed"
	@echo ""
	@echo "📦 Setting up Agent Chat UI..."
	@cd agent-chat-ui && pnpm install
	@echo "✅ Agent Chat UI dependencies installed"
	@echo ""
	@echo "🎉 Setup complete!"

start:
	@echo "🔄 Starting services..."
	@echo ""
	@echo "1️⃣  Starting PostgreSQL..."
	@cd aegra && docker compose up postgres -d
	@sleep 5
	@echo ""
	@echo "2️⃣  Running migrations..."
	@cd aegra && python3 scripts/migrate.py upgrade
	@echo ""
	@echo "3️⃣  Starting Aegra backend (http://localhost:8000)..."
	@echo "   In terminal 1, run: cd aegra && uv run uvicorn src.agent_server.main:app --reload"
	@echo ""
	@echo "4️⃣  Starting Agent Chat UI (http://localhost:3000)..."
	@echo "   In terminal 2, run: cd agent-chat-ui && pnpm dev"
	@echo ""
	@echo "✅ Ready! Open http://localhost:3000 in your browser"

start-docker:
	@echo "🐳 Starting all services with Docker..."
	docker compose -f docker-compose.all.yml up -d
	@echo ""
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 10
	@echo ""
	@echo "✅ Services running:"
	@echo "   - Aegra Backend: http://localhost:8000"
	@echo "   - Agent Chat UI: http://localhost:3000"
	@echo "   - PostgreSQL: localhost:5432"
	@echo ""
	@echo "View logs with: docker compose -f docker-compose.all.yml logs -f"

stop:
	@echo "🛑 Stopping local services..."
	@cd aegra && docker compose down

stop-docker:
	@echo "🛑 Stopping Docker services..."
	docker compose -f docker-compose.all.yml down

logs:
	@echo "📋 Service logs:"
	@echo ""
	@echo "Aegra logs:"
	@echo "  cd aegra && docker compose logs -f aegra"
	@echo ""
	@echo "Database logs:"
	@echo "  cd aegra && docker compose logs -f postgres"

logs-docker:
	docker compose -f docker-compose.all.yml logs -f

clean:
	@echo "🧹 Cleaning up..."
	@cd aegra && rm -rf .venv __pycache__ .pytest_cache .mypy_cache
	@cd agent-chat-ui && rm -rf node_modules .next
	@docker compose -f docker-compose.all.yml down -v
	@echo "✅ Cleanup complete"

test: test-backend test-frontend
	@echo "✅ All tests passed!"

test-backend:
	@echo "🧪 Testing Aegra backend..."
	@bash /home/test_integration.sh

test-frontend:
	@echo "🧪 Testing Agent Chat UI..."
	@echo "   Visit http://localhost:3000 in your browser"
	@echo "   Configure: API URL=http://localhost:8000, Assistant ID=agent"
	@echo "   Test: Send a message in the chat"

db-up:
	@echo "🗄️  Starting PostgreSQL..."
	@cd aegra && docker compose up postgres -d
	@echo "✅ PostgreSQL running on localhost:5432"

db-down:
	@echo "🛑 Stopping PostgreSQL..."
	@cd aegra && docker compose down

db-migrate:
	@echo "📦 Running database migrations..."
	@cd aegra && python3 scripts/migrate.py upgrade
	@echo "✅ Migrations complete"

db-reset:
	@echo "⚠️  Resetting database (this will delete all data)..."
	@read -p "Are you sure? (type 'yes' to confirm): " confirm && [ "$$confirm" = "yes" ] || exit 1
	@cd aegra && python3 scripts/migrate.py reset
	@echo "✅ Database reset complete"

# Development shortcuts
dev-aegra:
	@cd aegra && uv run uvicorn src.agent_server.main:app --reload --host 0.0.0.0 --port 8000

dev-ui:
	@cd agent-chat-ui && pnpm dev

# Quick test of OpenAI API
test-openai-api:
	@echo "Testing OpenAI-compatible API..."
	@echo ""
	@echo "1. Listing models:"
	@curl -s http://localhost:8000/v1/models | python3 -m json.tool
	@echo ""
	@echo "2. Chat completion:"
	@curl -s -X POST http://localhost:8000/v1/chat/completions \
	  -H "Content-Type: application/json" \
	  -d '{"model":"agent","messages":[{"role":"user","content":"Hello"}],"thread_id":"test-123"}' | python3 -m json.tool

# Production build
build:
	@echo "🏗️  Building for production..."
	@cd aegra && docker build -t aegra:latest .
	@cd agent-chat-ui && docker build -t agent-chat-ui:latest .
	@echo "✅ Build complete"
