from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent.parent


class AppSettings(BaseSettings):
    APP_NAME: str = "app"
    APP_TITLE: str = "FastAPI Base"
    APP_VERSION: str = "1"

    IS_DEBUG: bool = Field(default=True)
    BASE_URL: str = "http://localhost:8080"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class DBSettings(AppSettings):
    DB_URL: str = ""
    SQLITE_URL: str = "sqlite+aiosqlite:///db.sqlite3"

    POSTGRES_DB: str = "POSTGRES_DB"
    POSTGRES_USER: str = "POSTGRES_USER"
    POSTGRES_PASSWORD: str = "POSTGRES_PASSWORD"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    def get_pg_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def model_post_init(self, __context) -> None:
        if not self.DB_URL:
            object.__setattr__(
                self,
                "DB_URL",
                self.SQLITE_URL if self.IS_DEBUG else self.get_pg_url(),
            )


class CORSSettings(AppSettings):
    CORS_ORIGINS: list[str] = ["127.0.0.1", "localhost"]
    ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]


class LoggingSettings(AppSettings):
    LOG_LEVEL: str = "INFO"


class StorageSettings(AppSettings):
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET_NAME: str = ""
    AWS_S3_ENDPOINT_URL: str = ""
    AWS_DEFAULT_ACL: str = ""
    AWS_S3_USE_SSL: bool = True


class RedisSettings(AppSettings):
    REDIS_URL: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CONNECTION_POOL_MAXSIZE: int = 10
    EXPIRE: int = 3600

    def model_post_init(self, __context) -> None:
        if not self.REDIS_URL:
            object.__setattr__(
                self,
                "REDIS_URL",
                f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}",
            )


class UsersSettings(AppSettings):
    STRATEGY_SECRET_KEY: str
    RESET_SECRET_KEY: str
    VERIFICATION_SECRET_KEY: str
    LIFETIME_SECONDS: int = 3600
    TOKEN_URL: str = "auth/login"

    VERIFY_URL: str = "{base_url}/verify?token={token}"
    RESET_PASSWORD_URL: str = "{base_url}/reset-password?token={token}"


class MailSettings(AppSettings):
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "no-reply@example.com"
    MAIL_PORT: int = 1025
    MAIL_SERVER: str = "localhost"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = False
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = BASE_DIR / "templates" / "mail"


class RabbitMQSettings(AppSettings):
    RABBITMQ_URL: str = ""
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672

    def model_post_init(self, __context) -> None:
        if not self.RABBITMQ_URL:
            object.__setattr__(
                self,
                "RABBITMQ_URL",
                f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
                f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//",
            )


class TaskiqSettings(AppSettings):
    TASKIQ_RETRY_COUNT: int = 5
    TASKIQ_RETRY_DELAY: float | int = 10


class Settings(AppSettings):
    app: AppSettings = AppSettings()
    cors: CORSSettings = CORSSettings()
    db: DBSettings = DBSettings()
    logging: LoggingSettings = LoggingSettings()
    storage: StorageSettings = StorageSettings()
    redis: RedisSettings = RedisSettings()
    users: UsersSettings = UsersSettings()
    mail: MailSettings = MailSettings()
    rabbit: RabbitMQSettings = RabbitMQSettings()
    taskiq: TaskiqSettings = TaskiqSettings()


settings = Settings()
