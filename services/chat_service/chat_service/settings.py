import os
import enum
from pathlib import Path
from tempfile import gettempdir
from typing import List, Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings as PydanticBaseSettings, SettingsConfigDict

from yarl import URL

TEMP_DIR = Path(gettempdir())
PREFIX = "CHAT_SERVICE_"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class EnvLevel(enum.IntEnum):
    """Possible deployment environments."""

    local = enum.auto()
    sandbox = enum.auto()
    dev = enum.auto()
    qa = enum.auto()
    prod = enum.auto()


class PGSettingsRO(BaseSettings):
    """Configuration for database connection."""

    host: str = "localhost"

    port: int = 5432
    user: str = ""
    password: SecretStr = SecretStr("chat_service")
    database: str = ""
    pool_size: int = 15
    echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}PG_RO_",
    )

    @property
    def url(self) -> URL:
        """Assemble database URL from settings."""

        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password.get_secret_value(),
            path=f"/{self.database}",
        )


class PGSettingsWO(PGSettingsRO):
    """Configuration for database connection."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}PG_WO_",
    )


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    env: str = "local"

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for RabbitMQ
    rabbit_host: str = "chat_service-rmq"
    rabbit_port: int = 5672
    rabbit_user: str = "guest"
    rabbit_pass: str = "guest"
    rabbit_vhost: str = "/"

    rabbit_pool_size: int = 2
    rabbit_channel_pool_size: int = 10

    # PostgreSQL
    pg_ro: PGSettingsRO = PGSettingsRO()
    pg_wo: PGSettingsWO = PGSettingsWO()

    @property
    def env_level(self) -> EnvLevel:
        """Get environment level."""

        # check prod first
        for env_level in reversed(EnvLevel):
            if env_level.name in self.env:
                return env_level

        raise ValueError(f"Unknown environment: {self.env}. ")

    @property
    def rabbit_url(self) -> URL:
        """
        Assemble RabbitMQ URL from settings.

        :return: rabbit URL.
        """
        return URL.build(
            scheme="amqp",
            host=self.rabbit_host,
            port=self.rabbit_port,
            user=self.rabbit_user,
            password=self.rabbit_pass,
            path=self.rabbit_vhost,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=PREFIX,
        env_file_encoding="utf-8",
    )


settings = Settings()
