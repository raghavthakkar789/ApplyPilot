# ApplyPilot

ApplyPilot is a private, single-owner job discovery and application-preparation tool. The current Milestone 1 scaffold provides a synthetic Discover workspace, a FastAPI health boundary, an independent lifecycle-only worker, and private PostgreSQL infrastructure. Preparation never submits an application.

## Requirements

- Fedora with Docker Engine and the Docker Compose plugin installed
- Git
- A terminal opened in the ApplyPilot repository root

Check the required tools before starting:

```bash
docker --version
docker compose version
git --version
```

## Run the project for the first time

1. Create the ignored local environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and replace every placeholder password or secret with a strong local random value. Never commit `.env`.

3. Validate and build the canonical Compose runtime:

   ```bash
   docker compose config
   docker compose build
   ```

4. Start every service and wait for its health check:

   ```bash
   docker compose up -d --wait
   ```

5. Open `http://127.0.0.1:3000` in the local browser.

6. Confirm the services are healthy:

   ```bash
   docker compose ps
   curl --fail http://127.0.0.1:3000/api/health/live
   ```

Only the web service is available on the Fedora host, at `127.0.0.1:3000`. FastAPI, PostgreSQL, and the worker remain private inside Docker networks.

## Everyday runtime commands

```bash
# Start the already-built version
docker compose up -d --wait

# Follow service logs
docker compose logs -f

# Stop containers while preserving the PostgreSQL named volume
docker compose down
```

Do not add `--volumes` to the down command unless permanent deletion of local database storage is explicitly intended and an accepted backup is available.

## Save changes and run the new local version

Before rebuilding, inspect and validate the work being saved:

```bash
git status --short
git diff --check
git diff
```

Run the relevant tests. The complete current validation set is:

```bash
make check
docker compose config
docker compose build
```

If the checks pass, save the source revision in Git. Review the staged diff before committing, and never stage `.env`, private documents, credentials, or owner data:

```bash
git add <only-the-intended-files>
git diff --cached --check
git diff --cached
git commit -m "describe the completed change"
```

Rebuild and start that newly saved version:

```bash
docker compose down
docker compose build
docker compose up -d --wait
docker compose ps
```

Then reload `http://127.0.0.1:3000`. If only application code changed, the named PostgreSQL volume remains intact across this sequence.

### Run a newer version received from Git

First ensure `git status --short` is clean or commit the intended local work. Then update without creating an implicit merge commit and rebuild all service images:

```bash
git pull --ff-only
docker compose down
docker compose build
docker compose up -d --wait
docker compose ps
```

Do not run a data-altering migration until its required pre-migration encrypted backup has been completed and verified. Backup and migration automation are not implemented in the current scaffold.

Native Fedora execution may be used for debugging, but it is not a separately supported or acceptance-tested runtime.

## Service boundaries

- `apps/web`: Next.js 16.3.4, React 19.2.8, TypeScript 5.9.3, Tailwind CSS 4.3.3, Node.js 22.23.1, pnpm 10.6.5.
- `apps/api`: Python 3.13.15, FastAPI 0.115.12, Pydantic 2.11.1, SQLAlchemy 2.0.40, Alembic 1.15.2, psycopg 3.2.6, uv 0.12.3.
- `apps/worker`: independent Python 3.13.15 lifecycle boundary; no queue mechanism yet.
- `packages/api-client`: generated-contract boundary; the initial health type is checked in as generated output.
- `infra/docker`: infrastructure notes; service-specific Dockerfiles stay with each service.

## Validation

Use `make check` for the static and unit checks and `docker compose config` for Compose validation. Individual commands are documented in the Makefile. Docker Compose remains the canonical setup, build, and runtime interface.

Authentication, persistence models, source adapters, AI generation, background jobs, external submission, and real candidate data are intentionally absent from this slice. See [Progress](docs/PROGRESS.md) and [Roadmap](docs/DEVELOPMENT_ROADMAP.md).
