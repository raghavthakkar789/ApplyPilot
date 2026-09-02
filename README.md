# ApplyPilot

ApplyPilot is a private, single-owner job discovery and application-preparation tool. The current foundation provides atomic owner setup, password authentication, server-managed sessions, structured candidate facts, and protected versioned resume ingestion with deterministic PDF, DOCX, and UTF-8 text extraction. Preparation never submits an application.

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

   Environment files are backend runtime configuration only. Never place the
   owner's name, contact details, profile facts, resume text, login password,
   recovery phrases, session values, or CSRF values in them. Owner information
   is entered through authenticated Profile and Evidence flows and stored in
   PostgreSQL.

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

   On the first run, create the one local owner at `/setup`. Setup is permanently
   disabled after it succeeds. Later visits use `/login`.

6. Confirm the services are healthy:

   ```bash
   docker compose ps
   curl --fail http://127.0.0.1:3000/api/health/live
   ```

Only the web service is available on the Fedora host, at `127.0.0.1:3000`. FastAPI, PostgreSQL, and the worker remain private inside Docker networks.

Private resume originals live in the `document-data` Docker volume, outside
Git and the source tree. Do not copy that volume into the repository. The
current upload limit is 10 MiB; PDF, DOCX, and UTF-8 `.txt` are supported.

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

## Owner access and password recovery

Authentication uses a host-only HTTP-only session cookie. Do not copy browser
cookies, CSRF values, `.env`, or database credentials into commands, logs, or
Git. There is no web, email, or remote forgot-password flow. Passwords cannot
be retrieved or displayed: Argon2id stores only a one-way verifier, and
recovery replaces the password without revealing the old one.

If the owner password is lost, run the local-shell recovery command from the
repository root. It prompts twice using hidden input, changes the verifier
atomically, increments the credential version, and revokes every session:

```bash
docker compose run --rm api python -m applypilot.cli.reset_password
```

The command requires the database service to be running and authorized access
to the local Fedora account and ApplyPilot runtime.

## Service boundaries

- `apps/web`: Next.js 16.3.4, React 19.2.8, TypeScript 5.9.3, Tailwind CSS 4.3.3, Node.js 22.23.1, pnpm 10.6.5.
- `apps/api`: Python 3.13.15, FastAPI 0.115.12, Pydantic 2.11.1, SQLAlchemy 2.0.40, Alembic 1.15.2, psycopg 3.2.6, uv 0.12.3.
- `apps/worker`: independent Python 3.13.15 lifecycle boundary; no queue mechanism yet.
- `packages/api-client`: generated-contract boundary; the initial health type is checked in as generated output.
- `infra/docker`: infrastructure notes; service-specific Dockerfiles stay with each service.

## Validation

Use `make check` for static and unit checks and `docker compose config` for
Compose validation. Backend tests use the `test` profile and an unpublished,
tmpfs-backed PostgreSQL test service; they never target the live named volume.
Individual commands are documented in the Makefile. Docker Compose remains the
canonical setup, build, migration, recovery, and runtime interface.

Job persistence, source adapters, AI/OCR extraction, background jobs, external
submission, TOTP/MFA, and real candidate data are intentionally absent from
this slice. See [Progress](docs/PROGRESS.md) and
[Roadmap](docs/DEVELOPMENT_ROADMAP.md).
