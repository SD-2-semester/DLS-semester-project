from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


TEMP_DIR = Path(gettempdir())
PREFIX = "GATEWAY_"


class Settings(BaseSettings):
    """Application settings."""

    host: str = "127.0.0.1"
    port: int = 8086
    auth_service_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=PREFIX,
        env_file_encoding="utf-8",
    )


settings = Settings()
