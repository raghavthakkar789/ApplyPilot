from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://applypilot:placeholder@postgres:5432/applypilot"
    api_title: str = "ApplyPilot API"
    api_version: str = "0.1.0"
    allowed_origin: str = "http://127.0.0.1:3000"
    cookie_secure: bool = False

    @model_validator(mode="after")
    def validate_transport_boundary(self) -> "Settings":
        if self.allowed_origin != "http://127.0.0.1:3000" and not self.cookie_secure:
            raise ValueError("Non-loopback operation requires secure cookies")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
