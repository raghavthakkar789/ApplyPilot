from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from applypilot.models.csrf_token import SessionCsrfToken
from applypilot.models.owner_account import OwnerAccount
from applypilot.models.session import OwnerSession
from applypilot.repositories.database import SessionFactory
from tests.auth_helpers import ORIGIN, client, initialize, login, reset_auth_database


@pytest.fixture(autouse=True)
def clean_database() -> None:
    reset_auth_database()


def csrf_headers(test_client: object, origin: str = ORIGIN["Origin"]) -> dict[str, str]:
    token = test_client.cookies.get("applypilot_csrf")  # type: ignore[attr-defined]
    assert token
    return {"Origin": origin, "X-ApplyPilot-CSRF": token}


def test_csrf_success_missing_malformed_mismatch_and_origin() -> None:
    with client() as test_client:
        initialize(test_client)
        assert (
            test_client.post(
                "/api/sessions/revoke-others", headers=csrf_headers(test_client)
            ).status_code
            == 200
        )
        assert test_client.post("/api/sessions/revoke-others", headers=ORIGIN).status_code == 403
        assert (
            test_client.post(
                "/api/sessions/revoke-others", headers={**ORIGIN, "X-ApplyPilot-CSRF": "bad"}
            ).status_code
            == 403
        )
        assert (
            test_client.post(
                "/api/sessions/revoke-others",
                headers={**ORIGIN, "X-ApplyPilot-CSRF": generate_other_token()},
            ).status_code
            == 403
        )
        assert (
            test_client.post(
                "/api/sessions/revoke-others",
                headers=csrf_headers(test_client, "http://localhost:3000"),
            ).status_code
            == 403
        )
        assert (
            test_client.post(
                "/api/sessions/revoke-others",
                headers={**csrf_headers(test_client), "Host": "localhost:3000"},
            ).status_code
            == 400
        )
        assert (
            test_client.post(
                "/api/sessions/revoke-others",
                headers={
                    **csrf_headers(test_client),
                    "Host": "api:8000",
                    "X-Forwarded-Host": "127.0.0.1:3000",
                },
            ).status_code
            == 200
        )


def test_expired_csrf_token_is_rejected() -> None:
    with client() as test_client:
        initialize(test_client)
        headers = csrf_headers(test_client)
        with SessionFactory.begin() as database:
            verifier = database.scalar(select(SessionCsrfToken))
            assert verifier
            verifier.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        assert test_client.post("/api/sessions/revoke-others", headers=headers).status_code == 403


def generate_other_token() -> str:
    from applypilot.core.security import generate_token

    return generate_token()


def test_idle_and_absolute_expiry_and_activity_cap() -> None:
    with client() as test_client:
        initialize(test_client)
        with SessionFactory.begin() as database:
            session = database.scalar(select(OwnerSession))
            assert session
            session.idle_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        assert test_client.get("/api/auth/status").status_code == 401
    reset_auth_database()
    with client() as test_client:
        initialize(test_client)
        with SessionFactory.begin() as database:
            session = database.scalar(select(OwnerSession))
            assert session
            session.absolute_expires_at = datetime.now(UTC) - timedelta(seconds=1)
            session.idle_expires_at = datetime.now(UTC) + timedelta(minutes=30)
        assert test_client.get("/api/auth/status").status_code == 401
    reset_auth_database()
    with client() as test_client:
        initialize(test_client)
        with SessionFactory.begin() as database:
            session = database.scalar(select(OwnerSession))
            assert session
            session.absolute_expires_at = datetime.now(UTC) + timedelta(minutes=2)
            session.idle_expires_at = datetime.now(UTC) + timedelta(minutes=1)
            session.last_activity_at = datetime.now(UTC) - timedelta(minutes=6)
        assert test_client.get("/api/auth/status").status_code == 200
        with SessionFactory() as database:
            session = database.scalar(select(OwnerSession))
            assert session and session.idle_expires_at <= session.absolute_expires_at


def test_fourth_login_revokes_least_recent_session() -> None:
    with client() as first:
        initialize(first)
    clients = []
    for _ in range(3):
        item = client()
        item.__enter__()
        assert login(item).status_code == 200
        clients.append(item)
    try:
        with SessionFactory() as database:
            all_sessions = list(
                database.scalars(select(OwnerSession).order_by(OwnerSession.created_at))
            )
            assert len(all_sessions) == 4
            assert sum(session.revoked_at is None for session in all_sessions) == 3
            assert all_sessions[0].revocation_reason == "session_limit"
    finally:
        for item in clients:
            item.__exit__(None, None, None)


def test_logout_individual_revoke_others_and_credential_invalidation() -> None:
    with client() as first:
        initialize(first)
        with client() as second:
            login(second)
            sessions = second.get("/api/sessions").json()["sessions"]
            other = next(item for item in sessions if not item["current"])
            assert (
                second.delete(
                    f"/api/sessions/{other['id']}", headers=csrf_headers(second)
                ).status_code
                == 204
            )
            with client() as third:
                login(third)
                assert (
                    second.post("/api/sessions/revoke-others", headers=csrf_headers(second)).json()[
                        "revoked_count"
                    ]
                    == 1
                )
            assert second.post("/api/auth/logout", headers=csrf_headers(second)).status_code == 204
            assert second.get("/api/auth/status").status_code == 401
    reset_auth_database()
    with client() as test_client:
        initialize(test_client)
        with SessionFactory.begin() as database:
            owner = database.get(OwnerAccount, 1)
            assert owner
            owner.credential_version += 1
        assert test_client.get("/api/auth/status").status_code == 401
