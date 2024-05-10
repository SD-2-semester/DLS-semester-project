import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic import SecretStr
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())
PREFIX = "CHAT_SERVICE_"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class LogLevel(str, enum.Enum):
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


class PGSettings(BaseSettings):
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
        env_prefix=f"{PREFIX}PG_",
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


class PGSettingsRO(PGSettings):
    """Configuration for database connection."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}PG_RO_",
    )


class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    host: str = "chat_service-redis"
    port: int = 6379
    password: SecretStr | None = None

    @property
    def url(self) -> URL:
        """Redis URL."""
        return URL.build(
            scheme="redis",
            host=self.host,
            port=self.port,
            # password=self.password.get_secret_value() if self.password else None,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}REDIS_",
    )


class ElasticsearchSettings(BaseSettings):
    """Configuration for Elasticsearch."""

    cloud_id: str = "cloud_id"
    api_key: str = "api_key"
    host: str = "host.docker.internal"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}ELASTICSEARCH_",
    )


class RabbitMQSettings(BaseSettings):
    """Configuration for RabbitMQ."""

    host: str = "rabbitmq"
    port: int = 5672
    user: str = "user"
    password: SecretStr = SecretStr("password")
    vhost: str = "/"

    rabbit_pool_size: int = 2
    rabbit_channel_pool_size: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}RABBITMQ_",
    )

    @property
    def url(self) -> URL:
        """Assemble RabbitMQ URL from settings."""
        return URL.build(
            scheme="amqp",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password.get_secret_value(),
            path=self.vhost,
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

    auth_service_url: str = "http://localhost:8001"

    pg: PGSettings = PGSettings()
    pg_ro: PGSettingsRO = PGSettingsRO()

    redis: RedisSettings = RedisSettings()
    es: ElasticsearchSettings = ElasticsearchSettings()
    rabbit: RabbitMQSettings = RabbitMQSettings()

    @property
    def env_level(self) -> EnvLevel:
        """Get environment level."""

        # check prod first
        for env_level in reversed(EnvLevel):
            if env_level.name in self.env:
                return env_level

        raise ValueError(f"Unknown environment: {self.env}. ")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=PREFIX,
        env_file_encoding="utf-8",
    )


settings = Settings()
