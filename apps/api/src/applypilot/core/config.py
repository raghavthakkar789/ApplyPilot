from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    database_url: SecretStr
    api_title: str = "ApplyPilot API"
    api_version: str = "0.1.0"
    allowed_origin: str = "http://127.0.0.1:3000"
    cookie_secure: bool = False
    document_storage_root: str = "/var/lib/applypilot/documents"

    @model_validator(mode="after")
    def validate_security_boundaries(self) -> "Settings":
        database_url = self.database_url.get_secret_value()
        parsed_database = urlsplit(database_url)
        if (
            parsed_database.scheme != "postgresql+psycopg"
            or not parsed_database.hostname
            or not parsed_database.username
            or not parsed_database.password
            or parsed_database.path in {"", "/"}
        ):
            raise ValueError("DATABASE_URL must be a complete PostgreSQL psycopg DSN")
        if self.app_env == "production" and any(
            marker in database_url.casefold()
            for marker in ("placeholder", "replace-with", "test-only")
        ):
            raise ValueError("Production DATABASE_URL cannot contain a placeholder credential")
        parsed_origin = urlsplit(self.allowed_origin)
        if (
            parsed_origin.scheme not in {"http", "https"}
            or not parsed_origin.netloc
            or parsed_origin.path not in {"", "/"}
            or parsed_origin.query
            or parsed_origin.fragment
        ):
            raise ValueError("ALLOWED_ORIGIN must be one exact HTTP origin")
        if self.allowed_origin != "http://127.0.0.1:3000" and not self.cookie_secure:
            raise ValueError("Non-loopback operation requires secure cookies")
        if not Path(self.document_storage_root).is_absolute():
            raise ValueError("DOCUMENT_STORAGE_ROOT must be absolute")
        return self

    def database_dsn(self) -> str:
        """Reveal the database DSN only at the database integration boundary."""
        return self.database_url.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
