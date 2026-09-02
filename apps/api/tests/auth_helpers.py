from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import text

from applypilot.main import create_application
from applypilot.repositories.database import SessionFactory

ORIGIN = {"Origin": "http://127.0.0.1:3000"}
PASSWORD = "correct horse battery staple"


def reset_auth_database() -> None:
    with SessionFactory.begin() as database:
        database.execute(
            text(
                "TRUNCATE document_lifecycle_events, resume_fact_candidates, "
                "document_extractions, resume_versions, resumes, stored_documents, "
                "session_csrf_tokens, sessions, security_events, login_rate_limits, "
                "owner_account RESTART IDENTITY CASCADE"
            )
        )
        database.execute(text("UPDATE installation SET initialized_at = NULL WHERE id = 1"))


def client() -> TestClient:
    return TestClient(create_application(), headers={"Host": "127.0.0.1:3000"})


def initialize(test_client: TestClient, password: str = PASSWORD) -> object:
    return test_client.post(
        "/api/initialization",
        headers=ORIGIN,
        json={"password": password, "password_confirmation": password},
    )


def login(test_client: TestClient, password: str = PASSWORD) -> object:
    return test_client.post("/api/auth/login", headers=ORIGIN, json={"password": password})


def expire_login_throttle() -> None:
    with SessionFactory.begin() as database:
        database.execute(
            text(
                "UPDATE login_rate_limits SET blocked_until = :now WHERE rate_key = 'owner_login'"
            ),
            {"now": datetime.now(UTC)},
        )
