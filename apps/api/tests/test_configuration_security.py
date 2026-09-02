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
    }
    assert prohibited.isdisjoint(Settings.model_fields)


def test_transport_and_storage_configuration_fail_closed() -> None:
    with pytest.raises(ValidationError):
        settings(allowed_origin="http://example.test", cookie_secure=False)
    with pytest.raises(ValidationError):
        settings(allowed_origin="http://127.0.0.1:3000/path")
    with pytest.raises(ValidationError):
        settings(document_storage_root="relative/documents")
