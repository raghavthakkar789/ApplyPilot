import json

import pytest
from sqlalchemy import select

from applypilot.cli import import_owner_details_from_env, reset_password
from applypilot.models.candidate_fact import CandidateFactVersion
from applypilot.models.security_event import SecurityEvent
from applypilot.models.session import OwnerSession
from applypilot.repositories.database import SessionFactory
from applypilot.services.owner_details_import_service import (
    OwnerDetailsImportError,
    OwnerDetailsImportService,
)
from applypilot.services.password_recovery_service import PasswordRecoveryService
from tests.auth_helpers import ORIGIN, PASSWORD, client, initialize, login, reset_auth_database

SYNTHETIC_NAME = "Synthetic Owner"
SYNTHETIC_EMAIL = "synthetic.owner@example.test"


@pytest.fixture(autouse=True)
def clean_database() -> None:
    reset_auth_database()


def test_import_requires_initialized_owner() -> None:
    with SessionFactory() as database:
        with pytest.raises(OwnerDetailsImportError, match="initialized owner"):
            OwnerDetailsImportService(database).import_details(SYNTHETIC_NAME, SYNTHETIC_EMAIL)


def test_import_creates_unverified_facts_and_redacted_audit() -> None:
    with client() as test_client:
        initialize(test_client)
        login(test_client)
        with SessionFactory() as database:
            masked = OwnerDetailsImportService(database).import_details(
                SYNTHETIC_NAME, SYNTHETIC_EMAIL
            )
        assert SYNTHETIC_NAME not in masked["name"]
        assert SYNTHETIC_EMAIL not in masked["email"]
        profile = test_client.get("/api/profile")
        assert profile.status_code == 200
        sections = profile.json()["sections"]
        assert sections["identity"]["preferred_name"] == SYNTHETIC_NAME
        assert sections["contact"]["email"] == SYNTHETIC_EMAIL
        facts = test_client.get("/api/candidate-facts").json()["facts"]
        states = {
            item["semantic_key"]: item["current_version"]["lifecycle_state"] for item in facts
        }
        assert states["identity.preferred_name"] == "unverified"
        assert states["contact.email"] == "unverified"
        with SessionFactory() as database:
            confirmations = list(database.scalars(select(CandidateFactVersion)))
            assert all(version.owner_confirmed_at is None for version in confirmations)
            events = list(database.scalars(select(SecurityEvent)))
            imported = [event for event in events if event.event_type == "owner_details_imported"]
            assert imported
            serialized = json.dumps(imported[0].metadata_json)
            assert SYNTHETIC_NAME not in serialized
            assert SYNTHETIC_EMAIL not in serialized
            assert SYNTHETIC_NAME not in imported[0].event_type


def test_import_never_verifies_and_is_idempotent() -> None:
    with client() as test_client:
        initialize(test_client)
        with SessionFactory() as database:
            OwnerDetailsImportService(database).import_details(SYNTHETIC_NAME, SYNTHETIC_EMAIL)
            OwnerDetailsImportService(database).import_details(SYNTHETIC_NAME, SYNTHETIC_EMAIL)
        login(test_client)
        facts = test_client.get("/api/candidate-facts").json()["facts"]
        versions = {
            item["semantic_key"]: item["current_version"]["version_number"] for item in facts
        }
        assert versions["identity.preferred_name"] == 1
        assert versions["contact.email"] == 1
        assert all(item["current_version"]["lifecycle_state"] == "unverified" for item in facts)


def test_import_rejects_invalid_email() -> None:
    with client() as test_client:
        initialize(test_client)
        with SessionFactory() as database:
            with pytest.raises(OwnerDetailsImportError, match="could not be completed"):
                OwnerDetailsImportService(database).import_details(SYNTHETIC_NAME, "not-an-email")


def test_cli_import_uses_local_shell_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    with client() as test_client:
        initialize(test_client)
    monkeypatch.setattr(
        "sys.argv",
        [
            "import_owner_details_from_env",
            "--name",
            SYNTHETIC_NAME,
            "--email",
            SYNTHETIC_EMAIL,
            "--yes",
        ],
    )
    assert import_owner_details_from_env.main() == 0


def test_login_does_not_use_environment_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USER_PASSWORD", "env-password-must-be-ignored-xx")
    monkeypatch.setenv("PASSWORD_RESET_PHRASE", "env-phrase-must-be-ignored")
    with client() as test_client:
        initialize(test_client)
        assert login(test_client, "env-password-must-be-ignored-xx").status_code == 401
        assert login(test_client, PASSWORD).status_code == 200


def test_no_api_returns_password_or_verifier() -> None:
    with client() as test_client:
        initialize(test_client)
        login(test_client)
        for path in (
            "/api/auth/status",
            "/api/profile",
            "/api/sessions",
            "/api/candidate-facts",
            "/api/health/live",
            "/openapi.json",
        ):
            body = test_client.get(path).text
            folded = body.casefold()
            assert "password_verifier" not in folded
            assert "$argon2" not in folded
            assert PASSWORD not in body
        for path in (
            "/api/auth/forgot-password",
            "/api/auth/recover",
            "/api/password-reset",
            "/api/get-password",
        ):
            assert test_client.post(path, headers=ORIGIN, json={}).status_code == 404


def test_cli_password_reset_revokes_all_sessions(monkeypatch: pytest.MonkeyPatch) -> None:
    with client() as test_client:
        initialize(test_client)
        login(test_client)
    replacement = "new password from local shell only"
    monkeypatch.setattr("applypilot.cli.reset_password.getpass.getpass", lambda _: replacement)
    monkeypatch.setattr("sys.argv", ["reset_password"])
    assert reset_password.main() == 0
    with SessionFactory() as database:
        sessions = list(database.scalars(select(OwnerSession)))
        events = list(database.scalars(select(SecurityEvent)))
        assert sessions
        assert all(session.revoked_at is not None for session in sessions)
        assert any(event.event_type == "password_recovery" for event in events)
        serialized = json.dumps([event.metadata_json for event in events])
        assert replacement not in serialized
        assert PASSWORD not in serialized
    with client() as test_client:
        assert login(test_client, PASSWORD).status_code == 401
        assert login(test_client, replacement).status_code == 200


def test_recovery_service_still_revokes_sessions() -> None:
    with client() as test_client:
        initialize(test_client)
        login(test_client)
    replacement = "another local shell password"
    with SessionFactory() as database:
        PasswordRecoveryService(database).reset(replacement, replacement)
    with SessionFactory() as database:
        sessions = list(database.scalars(select(OwnerSession)))
        assert all(session.revoked_at is not None for session in sessions)
