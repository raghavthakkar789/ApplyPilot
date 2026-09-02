.PHONY: setup dev build test lint format check down logs

setup:
	docker compose build

dev:
	docker compose up --build

build:
	docker compose build

test:
	docker compose run --rm web pnpm test --run
	docker compose --profile test run --rm api-test
	docker compose run --rm worker uv run pytest

lint:
	docker compose run --rm web pnpm lint
	docker compose run --rm web pnpm typecheck
	docker compose --profile test run --rm --no-deps api-test ruff check src tests migrations
	docker compose --profile test run --rm --no-deps api-test mypy src
	docker compose run --rm worker uv run ruff check .

format:
	docker compose run --rm web pnpm format
	docker compose --profile test run --rm --no-deps api-test ruff format --check src tests migrations
	docker compose run --rm worker uv run ruff format .

check: lint test

down:
	docker compose down

logs:
	docker compose logs -f
