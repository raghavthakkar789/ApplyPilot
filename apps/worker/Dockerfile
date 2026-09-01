FROM python:3.13.15-slim-bookworm
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd --gid ${APP_GID} applypilot && useradd --uid ${APP_UID} --gid ${APP_GID} --create-home applypilot
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/src" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER applypilot
CMD ["python", "-m", "applypilot_worker.main"]
