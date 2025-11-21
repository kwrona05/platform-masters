from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


def _load_environment() -> None:
    """
    Mirror strategy from the CzasMuzykiAPI project:
    - on CI skip extra env files
    - locally pick .env.prod when CI_ENV=production else .env.dev
    - fall back to .env if present
    """
    ci_mode = os.getenv("CI")
    ci_env = os.getenv("CI_ENV")
    if not ci_mode:
        env_file = ".env.prod" if ci_env == "production" else ".env.dev"
        env_path = BASE_DIR / env_file
        if env_path.exists():
            load_dotenv(env_path)
            return
    # Fall back to .env (Render commonly injects env vars directly)
    default_env = BASE_DIR / ".env"
    if default_env.exists():
        load_dotenv(default_env)


def _resolve_database_url() -> str:
    url = os.getenv("DATABASE_URL")

    # Prefer explicit DATABASE_URL when provided (Render)
    if url:
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if url.startswith("sqlite:///"):
            return url
        return url

    # Local fallback to SQLite
    sqlite_name = "test.db" if os.getenv("APP_ENV") == "test" else "dev.db"
    return f"sqlite:///{BASE_DIR / sqlite_name}"


_load_environment()

DATABASE_URL = _resolve_database_url()
SQL_ECHO = os.getenv("SQL_DEBUG", "").lower() == "true"

# JWT / auth defaults (kept minimal; extend as needed)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# SMTP / Email
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER or "no-reply@example.com")

# CORS
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
