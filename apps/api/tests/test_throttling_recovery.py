import pytest
from sqlalchemy import select

from applypilot.models.login_rate_limit import LoginRateLimit
from applypilot.models.owner_account import OwnerAccount
from applypilot.models.security_event import SecurityEvent
from applypilot.models.session import OwnerSession
from applypilot.repositories.database import SessionFactory
from applypilot.services.password_recovery_service import PasswordRecoveryService
from tests.auth_helpers import (
    ORIGIN,
    client,
    expire_login_throttle,
    initialize,
    login,
    reset_auth_database,
)


@pytest.fixture(autouse=True)
def clean_database() -> None:
    reset_auth_database()


def test_login_backoff_sequence_and_no_permanent_lockout() -> None:
    with client() as test_client:
        initialize(test_client)
        for failure in range(1, 11):
            response = login(test_client, "incorrect but long password")
            if failure < 5:
                assert response.status_code == 401
            else:
                expected = [30, 60, 120, 240, 480, 900][min(failure - 5, 5)]
                assert response.status_code == 429
                assert int(response.headers["Retry-After"]) == expected
                expire_login_throttle()
        expire_login_throttle()
        assert login(test_client).status_code == 200
        with SessionFactory() as database:
            limiter = database.get(LoginRateLimit, "owner_login")
            assert limiter and limiter.consecutive_failures == 0 and limiter.blocked_until is None


def test_successful_login_resets_earlier_failures_and_failures_are_generic() -> None:
    with client() as test_client:
        uninitialized = login(test_client, "incorrect but long password")
        assert uninitialized.status_code == 401
        assert uninitialized.json()["detail"] == "Authentication could not be completed."
        reset_auth_database()
        initialize(test_client)
        wrong = login(test_client, "incorrect but long password")
        assert wrong.status_code == 401
        assert wrong.json()["detail"] == uninitialized.json()["detail"]
        too_long = login(test_client, "x" * 1025)
        assert too_long.status_code == 401
        assert too_long.json()["detail"] == uninitialized.json()["detail"]
        assert login(test_client).status_code == 200


def test_recovery_revokes_sessions_increments_credentials_and_ignores_http_throttle() -> None:
    with client() as test_client:
        initialize(test_client)
        for _ in range(5):
            login(test_client, "incorrect but long password")
        with SessionFactory() as database:
            before = database.get(OwnerAccount, 1)
            assert before
            version = before.credential_version
        new_password = "new password from local shell only"
        with SessionFactory() as database:
            PasswordRecoveryService(database).reset(new_password, new_password)
        with SessionFactory() as database:
            owner = database.get(OwnerAccount, 1)
            sessions = list(database.scalars(select(OwnerSession)))
            events = list(database.scalars(select(SecurityEvent)))
            assert owner and owner.credential_version == version + 1
            assert all(session.revoked_at is not None for session in sessions)
            assert any(event.event_type == "password_recovery" for event in events)
        expire_login_throttle()
        assert login(test_client, new_password).status_code == 200


def test_no_http_password_recovery_route_exists() -> None:
    with client() as test_client:
        for path in ("/api/auth/forgot-password", "/api/auth/recover", "/api/password-reset"):
            assert test_client.post(path, headers=ORIGIN, json={}).status_code == 404
