# ApplyPilot

ApplyPilot is a private, single-owner job discovery and application-preparation tool. The current Milestone 1 scaffold provides a synthetic Discover workspace, a FastAPI health boundary, an independent lifecycle-only worker, and private PostgreSQL infrastructure. Preparation never submits an application.

## Canonical local runtime

1. Copy `.env.example` to `.env` and replace every placeholder with a local random value.
2. Run `docker compose build`.
3. Run `docker compose up --wait`.
4. Open `http://127.0.0.1:3000`.
5. Stop with `docker compose down`.

Only the web service publishes a default host port. FastAPI, PostgreSQL, and the worker remain on the private Compose network. Native commands are debugging aids, not a supported deployment.

## Service boundaries

- `apps/web`: Next.js 16.3.4, React 19.2.8, TypeScript 5.9.3, Tailwind CSS 4.3.3, Node.js 22.23.1, pnpm 10.6.5.
- `apps/api`: Python 3.13.15, FastAPI 0.115.12, Pydantic 2.11.1, SQLAlchemy 2.0.40, Alembic 1.15.2, psycopg 3.2.6, uv 0.12.3.
- `apps/worker`: independent Python 3.13.15 lifecycle boundary; no queue mechanism yet.
- `packages/api-client`: generated-contract boundary; the initial health type is checked in as generated output.
- `infra/docker`: infrastructure notes; service-specific Dockerfiles stay with each service.

## Validation

Use `make check` for local static/unit checks and `make compose-check` for Compose validation. Individual commands are documented in the Makefile. Docker Compose remains the canonical setup, build, and runtime interface.

Authentication, persistence models, source adapters, AI generation, background jobs, external submission, and real candidate data are intentionally absent from this slice. See [Progress](docs/PROGRESS.md) and [Roadmap](docs/DEVELOPMENT_ROADMAP.md).
