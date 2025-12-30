.PHONY: help install test run docker-build docker-up docker-down init-db migrate

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make run          - Run the service locally"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start service with Docker Compose"
	@echo "  make docker-down  - Stop service"
	@echo "  make init-db      - Initialize database schema"
	@echo "  make migrate      - Run database migrations"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

docker-build:
	docker build -t prioritest-collecte-depots .

docker-up:
	docker-compose up -d collecte-depots

docker-down:
	docker-compose down

init-db:
	python scripts/init_db.py

migrate:
	alembic upgrade head

