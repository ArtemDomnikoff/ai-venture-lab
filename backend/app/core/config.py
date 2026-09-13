from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "AI Venture Lab"
    app_env: str = "development"

    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = "venture_lab"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def async_database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return (
            f"redis://{self.redis_host}:{self.redis_port}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()