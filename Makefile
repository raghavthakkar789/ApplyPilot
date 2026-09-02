.PHONY: help setup dev build test lint typecheck format security-scan check down logs

help:
	@echo "ApplyPilot commands (Docker Compose is canonical):"
	@echo "  make setup          Build service images"
	@echo "  make dev            Start the development stack with builds"
	@echo "  make build          Build service images"
	@echo "  make test           Run web, API, and worker tests"
	@echo "  make lint           Run frontend/API/worker lint and type checks"
	@echo "  make typecheck      Run frontend and API type checks"
	@echo "  make format         Check or apply repository formatters"
	@echo "  make security-scan  Check environment and secret boundaries"
	@echo "  make check          Run lint, tests, and security scan"
	@echo "  make down           Stop containers without deleting volumes"
	@echo "  make logs           Follow Compose logs"

setup:
	docker compose build

dev:
	docker compose up --build

build:
	docker compose build

test:
	docker compose --profile test run --rm --no-deps web-test pnpm test --run
	docker compose --profile test run --rm api-test
	docker compose --profile test run --rm --no-deps worker-test

lint:
	./scripts/check-lint-runtime.sh
	docker compose --profile test run --rm --no-deps web-test pnpm lint
	docker compose --profile test run --rm --no-deps web-test pnpm typecheck
	docker compose --profile test run --rm --no-deps api-test ruff check src tests migrations
	docker compose --profile test run --rm --no-deps api-test mypy src
	docker compose --profile test run --rm --no-deps worker-test ruff check .

typecheck:
	docker compose --profile test run --rm --no-deps web-test pnpm typecheck
	docker compose --profile test run --rm --no-deps api-test mypy src

format:
	docker compose --profile test run --rm --no-deps web-test pnpm format
	docker compose --profile test run --rm --no-deps api-test ruff format --check src tests migrations
	docker compose --profile test run --rm --no-deps worker-test ruff format .

security-scan:
	./scripts/check-security-boundaries.sh

check: lint test security-scan

down:
	docker compose down

logs:
	docker compose logs -f
