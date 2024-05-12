from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from enum import StrEnum, auto

TEMP_DIR = Path(gettempdir())
PREFIX = "GATEWAY_"


class Environment(StrEnum):
    """Application environment."""

    local = auto()
    cluster = auto()


class Settings(BaseSettings):
    """Application settings."""

    environment: Environment = Environment.local

    host: str = "127.0.0.1"
    port: int = 8086
    auth_url: str = "http://localhost:8080"
    chat_url: str = "http://localhost:8085"
    relation_url: str = "http://localhost:8000"
    notification_url: str = "http://localhost:8081"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=PREFIX,
        env_file_encoding="utf-8",
    )

    def get_service_url(self, service_name: str) -> str:
        service_map = {
            "auth": self.auth_url,
            "chat": self.chat_url,
            "relation": self.relation_url,
            "notification": self.notification_url,
        }
        url = service_map.get(service_name, None)

        if not url:
            raise ValueError(f"Service {service_name} not found")

        return f"{url}/{service_name}"


settings = Settings()
