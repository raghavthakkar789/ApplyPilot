import os

os.environ["APP_ENV"] = "test"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://applypilot_test:test-only-password@postgres-test:5432/applypilot_test",
)
