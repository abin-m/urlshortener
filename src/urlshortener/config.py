from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_prefix="URLSHORTENER_",
        frozen=True,
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+psycopg://urlshortener:urlshortener@localhost:5432/urlshortener",
        description="PostgreSQL connection string (SQLAlchemy URL, psycopg3 driver).",
    )
    host: str = Field(default="127.0.0.1", description="Bind address.")
    port: int = Field(default=8000, ge=1, le=65535, description="Bind port.")
    base_url: str = Field(
        default="http://localhost:8000",
        description="Public base URL used when building short links.",
    )
    code_length: int = Field(
        default=7, ge=4, le=32, description="Length of generated short codes."
    )
    log_level: str = Field(default="INFO", description="Root log level.")
