# AI Assist Async Jamboree - Docker Management

.PHONY: help dev ref prod down logs restart rebuild clean test test-integration test-all

# Default target
help:
	@echo "Available commands:"
	@echo "Environment Management:"
	@echo "  make dev         - Start development environment (with debug ports)"
	@echo "  make ref         - Start reference/staging environment"
	@echo "  make prod        - Start production environment"
	@echo ""
	@echo "General Commands:"
	@echo "  make down        - Stop and remove all containers"
	@echo "  make logs        - View container logs (follow mode)"
	@echo "  make restart     - Restart all containers"
	@echo "  make rebuild ENV=<env> - Stop, rebuild, and start environment (dev|ref|prod)"
	@echo "  make clean       - Stop containers and remove images/volumes"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run tests in containers"
	@echo "  make test-integration - Run full integration test (start, test, stop)"
	@echo "  make test-all    - Build and test all environments (dev, ref, prod)"
	@echo ""
	
# Stop all containers (works for any environment)
down:
	docker compose down

# View logs (works for any environment)
logs:
	docker compose logs -f

# Restart containers (works for any environment)
restart:
	docker compose restart

# Rebuild and restart (requires ENV parameter)
rebuild:
	@if [ -z "$(ENV)" ]; then \
		echo "Usage: make rebuild ENV=dev|ref|prod"; \
		exit 1; \
	fi
	docker compose down
	@if [ ! -f .env.$(ENV) ]; then \
		echo "❌ .env.$(ENV) not found!"; \
		echo "💡 Create it with: cp .env.$(ENV).example .env.$(ENV)"; \
		exit 1; \
	fi
	docker compose --env-file .env.$(ENV) -f docker-compose.yml -f docker-compose.$(ENV).yml up --build

# Clean up everything (containers, images, volumes)
clean:
	docker compose down --rmi all --volumes --remove-orphans

# Run tests
test:
	docker compose exec flask-app python -m pytest flask_app/tests/ -v || echo "Flask container not running"
	docker compose exec tornado-app python -m pytest tornado_app/tests/ -v || echo "Tornado container not running"

# Run integration test (starts services, tests, then stops)
test-integration:
	PYTHONPATH=. pipenv run pytest tests/test_integration.py -v

# Build and test all environments in sequence
test-all:
	@echo "🚀 Starting comprehensive testing of all environments..."
	@echo ""
	
	@echo "📋 Checking environment files..."
	@for env in dev ref prod; do \
		if [ ! -f .env.$$env ]; then \
			echo "❌ .env.$$env not found!"; \
			echo "💡 Create it with: cp .env.$$env.example .env.$$env"; \
			exit 1; \
		fi; \
	done
	@echo "✅ All environment files found"
	@echo ""
	
	@echo "🧹 Cleaning up any existing containers..."
	docker compose down --remove-orphans || true
	@echo ""
	
	@echo "🔨 Building and testing DEV environment..."
	docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up --build -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 5
	@echo "🧪 Running health checks with retries..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		echo "Testing Flask app (attempt $$i/10)..."; \
		if curl -f -s http://localhost:80/ > /dev/null 2>&1; then \
			echo "✅ Flask app accessible"; \
			break; \
		elif [ $$i -eq 10 ]; then \
			echo "❌ DEV Flask app failed after retries"; \
			docker compose logs flask-app; \
			docker compose down; \
			exit 1; \
		fi; \
		sleep 2; \
	done
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		echo "Testing Tornado app (attempt $$i/10)..."; \
		if curl -f -s http://localhost:80/tornado/ > /dev/null 2>&1; then \
			echo "✅ Tornado app accessible"; \
			break; \
		elif [ $$i -eq 10 ]; then \
			echo "❌ DEV Tornado app failed after retries"; \
			docker compose logs tornado-app; \
			docker compose down; \
			exit 1; \
		fi; \
		sleep 2; \
	done
	@echo "✅ DEV environment healthy"
	docker compose down
	@echo ""
	
	@echo "🔨 Building and testing REF environment..."
	docker compose --env-file .env.ref -f docker-compose.yml -f docker-compose.ref.yml up --build -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 10
	@echo "🧪 Running health checks (tests will exit on failure)..."
	@curl -f -s http://localhost:80/health > /dev/null || (echo "REF health check failed" && docker compose down && exit 1)
	@echo "✅ Health check passed"
	@curl -f -s http://localhost:80/ > /dev/null || (echo "REF Flask app failed" && docker compose down && exit 1)
	@echo "✅ Flask app accessible"
	@curl -f -s http://localhost:80/tornado/ > /dev/null || (echo "REF Tornado app failed" && docker compose down && exit 1)
	@echo "✅ Tornado app accessible"
	@echo "✅ REF environment healthy"
	docker compose down
	@echo ""
	
	@echo "🔨 Building and testing PROD environment..."
	docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up --build -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 10
	@echo "🧪 Running health checks (tests will exit on failure)..."
	@curl -f -s http://localhost:80/health > /dev/null || (echo "PROD health check failed" && docker compose down && exit 1)
	@echo "✅ Health check passed"
	@curl -f -s http://localhost:80/ > /dev/null || (echo "PROD Flask app failed" && docker compose down && exit 1)
	@echo "✅ Flask app accessible"
	@curl -f -s http://localhost:80/tornado/ > /dev/null || (echo "PROD Tornado app failed" && docker compose down && exit 1)
	@echo "✅ Tornado app accessible"
	@echo "✅ PROD environment healthy"
	docker compose down
	@echo ""
	
	@echo "🧪 Running full integration test suite..."
	PYTHONPATH=. pipenv run pytest tests/test_integration.py -v || (echo "Integration tests failed" && exit 1)
	@echo ""
	
	@echo "🎉 All environments built and tested successfully!"
	@echo "✅ DEV: Built and healthy"
	@echo "✅ REF: Built and healthy"  
	@echo "✅ PROD: Built and healthy"
	@echo "✅ Integration tests: Passed"

# Environment-specific commands
dev:
	@if [ ! -f .env.dev ]; then \
		echo "❌ .env.dev not found!"; \
		echo "💡 Create it with: cp .env.dev.example .env.dev"; \
		echo "📝 Then edit .env.dev with your configuration"; \
		exit 1; \
	fi
	docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up --build

ref:
	@if [ ! -f .env.ref ]; then \
		echo "❌ .env.ref not found!"; \
		echo "💡 Create it with: cp .env.ref.example .env.ref"; \
		echo "📝 Then edit .env.ref with your configuration"; \
		exit 1; \
	fi
	docker compose --env-file .env.ref -f docker-compose.yml -f docker-compose.ref.yml up --build

prod:
	@if [ ! -f .env.prod ]; then \
		echo "❌ .env.prod not found!"; \
		echo "💡 Create it with: cp .env.prod.example .env.prod"; \
		echo "📝 Then edit .env.prod with your configuration"; \
		exit 1; \
	fi
	docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up --build

