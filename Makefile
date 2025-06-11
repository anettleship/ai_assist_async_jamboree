# AI Assist Async Jamboree - Docker Management

.PHONY: help up down logs restart build clean test test-integration dev-setup

# Default target
help:
	@echo "Available commands:"
	@echo "  make up          - Start all containers (build if needed)"
	@echo "  make down        - Stop and remove all containers"
	@echo "  make logs        - View container logs (follow mode)"
	@echo "  make restart     - Restart all containers"
	@echo "  make build       - Build containers without starting"
	@echo "  make clean       - Stop containers and remove images/volumes"
	@echo "  make test        - Run tests in containers"
	@echo "  make test-integration - Run full integration test (start, test, stop)"
	@echo "  make dev-setup   - Setup development environment"

# Start all containers
up:
	docker compose up --build

# Start containers in background
up-bg:
	docker compose up --build -d

# Stop all containers
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Restart containers
restart:
	docker compose restart

# Build containers only
build:
	docker compose build

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

# Development setup (local)
dev-setup:
	pipenv install --dev
	@echo "Development environment ready!"
	@echo "Run 'pipenv shell' to activate virtual environment"