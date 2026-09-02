from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import func, select, text

from applypilot.core.security import generate_token, hash_password, hash_token, verify_password
from applypilot.models.owner_account import OwnerAccount
from applypilot.models.security_event import SecurityEvent
from applypilot.models.session import OwnerSession
from applypilot.repositories.database import SessionFactory
from tests.auth_helpers import ORIGIN, PASSWORD, client, initialize, reset_auth_database


@pytest.fixture(autouse=True)
def clean_database() -> None:
    reset_auth_database()


def test_twenty_concurrent_initializations_create_exactly_one_owner() -> None:
    def attempt(_: int) -> int:
        with client() as test_client:
            return initialize(test_client).status_code  # type: ignore[union-attr]

    with ThreadPoolExecutor(max_workers=20) as pool:
        statuses = list(pool.map(attempt, range(20)))
    assert statuses.count(201) == 1
    assert set(statuses).issubset({201, 404})
    with SessionFactory() as database:
        assert database.scalar(select(func.count()).select_from(OwnerAccount)) == 1


def test_initialization_is_unavailable_after_success_and_hash_is_never_returned() -> None:
    with client() as test_client:
        response = initialize(test_client)
        assert response.status_code == 201
        assert "password" not in response.text.lower()
        assert initialize(test_client).status_code == 404
        assert test_client.get("/api/initialization/status").json() == {"required": False}


def test_password_hashing_and_token_entropy() -> None:
    verifier = hash_password(PASSWORD)
    assert verifier.startswith("$argon2id$")
    assert verify_password(verifier, PASSWORD)
    assert not verify_password(verifier, "incorrect password")
    token = generate_token()
    assert len(__import__("base64").urlsafe_b64decode(token + "==")) >= 32


def test_initialization_is_limited_to_three_attempts_per_five_minutes() -> None:
    with client() as test_client:
        for _ in range(3):
            response = test_client.post(
                "/api/initialization",
                headers=ORIGIN,
                json={"password": "short", "password_confirmation": "short"},
            )
            assert response.status_code == 400
        response = initialize(test_client)
        assert response.status_code == 429
        assert 1 <= int(response.headers["Retry-After"]) <= 300


def test_raw_tokens_are_absent_from_database_and_cookie_is_host_only() -> None:
    with client() as test_client:
        response = initialize(test_client)
        raw_session = test_client.cookies.get("applypilot_session")
        raw_csrf = test_client.cookies.get("applypilot_csrf")
        assert raw_session and raw_csrf
        cookie = response.headers["set-cookie"]
        assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Path=/" in cookie
        assert "Domain=" not in cookie and "Secure" not in cookie
        with SessionFactory() as database:
            stored = database.scalar(select(OwnerSession))
            assert stored and stored.token_hash == hash_token(raw_session)
            dump = " ".join(str(row) for row in database.execute(text("SELECT * FROM sessions")))
            assert raw_session not in dump and raw_csrf not in dump


def test_security_events_are_redacted() -> None:
    with client() as test_client:
        initialize(test_client)
        test_client.post("/api/auth/login", headers=ORIGIN, json={"password": "wrong-password"})
    with SessionFactory() as database:
        events = list(database.scalars(select(SecurityEvent)))
        serialized = " ".join(str(event.metadata_json) for event in events)
        assert PASSWORD not in serialized
        assert "wrong-password" not in serialized
        assert all("token" not in str(event.metadata_json).lower() for event in events)
