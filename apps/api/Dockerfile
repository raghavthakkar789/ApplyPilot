FROM python:3.13.15-slim-bookworm AS base

ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd --gid ${APP_GID} applypilot && useradd --uid ${APP_UID} --gid ${APP_GID} --create-home applypilot
RUN install -d -o applypilot -g applypilot -m 0700 /var/lib/applypilot/documents
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock alembic.ini ./

FROM base AS runtime
COPY migrations ./migrations
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/src" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER applypilot
EXPOSE 8000
CMD ["uvicorn", "applypilot.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test
COPY migrations ./migrations
COPY src ./src
COPY tests ./tests
RUN uv sync --frozen --dev --no-editable
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/src" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER applypilot
CMD ["pytest", "-q"]
