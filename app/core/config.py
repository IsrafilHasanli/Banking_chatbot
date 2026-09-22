from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None else int(value)


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None else float(value)


@dataclass(frozen=True)
class Settings:
    AUTH_PROVIDER: str = os.getenv("AUTH_PROVIDER", "aws").lower()

    CLAUDE_API_KEY: str | None = os.getenv("CLAUDE_API_KEY")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")

    DB_HOST: str | None = os.getenv("DB_HOST")
    DB_NAME: str | None = os.getenv("DB_NAME")
    DB_USER: str | None = os.getenv("DB_USER")
    DB_PASS: str | None = os.getenv("DB_PASS")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    SQLALCHEMY_ECHO: bool = _get_bool("SQLALCHEMY_ECHO", False)

    AWS_CLIENT_ID: str | None = os.getenv("AWS_CLIENT_ID")
    AWS_REGION: str | None = os.getenv("AWS_REGION")
    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_USER_POOL_ID: str | None = os.getenv("AWS_USER_POOL_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")

    SMTP_SERVER: str | None = os.getenv("SMTP_SERVER")
    MAIL_USER: str | None = os.getenv("MAIL_USER")
    MAIL_PASS: str | None = os.getenv("MAIL_PASS")

    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = _get_int("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    CHAT_CACHE_ENABLED: bool = _get_bool("CHAT_CACHE_ENABLED", True)
    CHAT_CACHE_TTL_SECONDS: int = _get_int("CHAT_CACHE_TTL_SECONDS", 3600)
    CHAT_SEMANTIC_CACHE_ENABLED: bool = _get_bool("CHAT_SEMANTIC_CACHE_ENABLED", True)
    CHAT_SEMANTIC_CACHE_THRESHOLD: float = _get_float("CHAT_SEMANTIC_CACHE_THRESHOLD", 0.80)

    QDRANT_URL: str | None = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str | None = os.getenv("QDRANT_API_KEY")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        required = {
            "DB_HOST": self.DB_HOST,
            "DB_NAME": self.DB_NAME,
            "DB_USER": self.DB_USER,
            "DB_PASS": self.DB_PASS,
            "DB_PORT": self.DB_PORT,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing database configuration: {', '.join(missing)}")

        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def asyncpg_database_url(self) -> str:
        return self.sqlalchemy_database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    def validate(self) -> None:
        if self.AUTH_PROVIDER not in {"aws", "postgres"}:
            raise RuntimeError("AUTH_PROVIDER must be 'aws' or 'postgres'")

        self.sqlalchemy_database_url

        if not self.CLAUDE_API_KEY:
            raise RuntimeError("CLAUDE_API_KEY is required for the banking agent")

        if self.AUTH_PROVIDER == "aws":
            missing = [
                name
                for name, value in {
                    "AWS_CLIENT_ID": self.AWS_CLIENT_ID,
                    "AWS_REGION": self.AWS_REGION,
                    "AWS_USER_POOL_ID": self.AWS_USER_POOL_ID,
                }.items()
                if not value
            ]
            if missing:
                raise RuntimeError(f"Missing AWS Cognito configuration: {', '.join(missing)}")

        if self.AUTH_PROVIDER == "postgres" and not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY is required when AUTH_PROVIDER=postgres")

        if self.CHAT_SEMANTIC_CACHE_ENABLED and not self.QDRANT_URL:
            raise RuntimeError("QDRANT_URL is required when CHAT_SEMANTIC_CACHE_ENABLED=true")


settings = Settings()
