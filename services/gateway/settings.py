import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic import SecretStr
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())
PREFIX = "GATEWAY_"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    """Application settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    auth_service_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=PREFIX,
        env_file_encoding="utf-8",
    )


settings = Settings()
