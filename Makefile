.PHONY: setup dev build test lint format check down logs

setup:
	docker compose build

dev:
	docker compose up --build

build:
	docker compose build

test:
	docker compose run --rm web pnpm test --run
	docker compose run --rm api uv run pytest
	docker compose run --rm worker uv run pytest

lint:
	docker compose run --rm web pnpm lint
	docker compose run --rm web pnpm typecheck
	docker compose run --rm api uv run ruff check .
	docker compose run --rm api uv run mypy src tests
	docker compose run --rm worker uv run ruff check .

format:
	docker compose run --rm web pnpm format
	docker compose run --rm api uv run ruff format .
	docker compose run --rm worker uv run ruff format .

check: lint test

down:
	docker compose down

logs:
	docker compose logs -f
