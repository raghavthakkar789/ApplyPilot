from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://applypilot:placeholder@postgres:5432/applypilot"
    api_title: str = "ApplyPilot API"
    api_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
