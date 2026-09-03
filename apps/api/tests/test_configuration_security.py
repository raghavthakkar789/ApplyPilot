import os

import pytest
from pydantic import SecretStr, ValidationError

from applypilot.core.config import Settings

VALID_DATABASE_URL = (
    "postgresql+psycopg://synthetic_owner:synthetic-test-password@postgres:5432/applypilot"
)


def settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "database_url": VALID_DATABASE_URL,
        "app_env": "test",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


def test_database_configuration_is_required() -> None:
    previous = os.environ.pop("DATABASE_URL", None)
    try:
        with pytest.raises(ValidationError):
            Settings(_env_file=None)
    finally:
        if previous is not None:
            os.environ["DATABASE_URL"] = previous


def test_database_secret_is_redacted_from_settings_representation() -> None:
    configured = settings()
    assert isinstance(configured.database_url, SecretStr)
    assert VALID_DATABASE_URL not in repr(configured)
    assert "synthetic-test-password" not in str(configured.model_dump())


@pytest.mark.parametrize(
    "database_url",
    [
        "not-a-database-url",
        "postgresql+psycopg://postgres/applypilot",
        "postgresql://owner:password@postgres/applypilot",
    ],
)
def test_database_configuration_format_fails_closed(database_url: str) -> None:
    with pytest.raises(ValidationError):
        settings(database_url=database_url)


def test_production_rejects_placeholder_database_credentials() -> None:
    with pytest.raises(ValidationError):
        settings(
            app_env="production",
            database_url="postgresql+psycopg://owner:replace-with-secret@postgres/applypilot",
        )


def test_settings_schema_contains_no_owner_profile_or_recovery_fields() -> None:
    prohibited = {
        "owner_name",
        "owner_email",
        "owner_phone",
        "resume_content",
        "original_password",
        "forgot_password_phrase",
        "recovery_phrase",
        "session_token",
        "csrf_token",
        "user_name",
        "user_email",
        "user_password",
        "password_reset_phrase",
        "owner_password",
        "get_password",
    }
    assert prohibited.isdisjoint(Settings.model_fields)


def test_startup_ignores_environment_passwords_and_phrases(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USER_PASSWORD", "env-password-must-be-ignored-xx")
    monkeypatch.setenv("PASSWORD_RESET_PHRASE", "env-phrase-must-be-ignored")
    monkeypatch.setenv("OWNER_PASSWORD", "env-owner-password-must-be-ignored")
    configured = settings()
    dumped = configured.model_dump()
    rendered = repr(configured)
    assert "user_password" not in dumped
    assert "password_reset_phrase" not in dumped
    assert "env-password-must-be-ignored-xx" not in rendered
    assert "env-phrase-must-be-ignored" not in rendered


def test_env_example_contains_no_personal_or_recoverable_password_fields() -> None:
    from pathlib import Path

    here = Path(__file__).resolve()
    candidates = [Path.cwd() / ".env.example"]
    candidates.extend(parent / ".env.example" for parent in here.parents)
    example = next((path for path in candidates if path.is_file()), None)
    if example is None:
        pytest.skip("Repository .env.example is not mounted in the API test image")
    text = example.read_text()
    for banned in (
        "USER_" "PASSWORD",
        "PASSWORD_" "RESET_PHRASE",
        "OWNER_" "PASSWORD",
        "GET_" "PASSWORD",
        "RECOVERY_" "PHRASE",
        "USER_" "NAME",
        "USER_" "EMAIL",
        "NEXT_PUBLIC_" "USER_",
        "@" "gmail.",
    ):
        assert banned not in text


def test_transport_and_storage_configuration_fail_closed() -> None:
    with pytest.raises(ValidationError):
        settings(allowed_origin="http://example.test", cookie_secure=False)
    with pytest.raises(ValidationError):
        settings(allowed_origin="http://127.0.0.1:3000/path")
    with pytest.raises(ValidationError):
        settings(document_storage_root="relative/documents")
