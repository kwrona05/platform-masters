from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, inspect, text

from config import DATABASE_URL
from database import Base, engine
from utils.logger import logger

BASE_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_INI = BASE_DIR / "alembic.ini"
ALEMBIC_SCRIPT_DIR = BASE_DIR / "alembic"


def _alembic_config() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(ALEMBIC_SCRIPT_DIR))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    cfg.attributes["configure_logger"] = False
    return cfg


def ensure_database() -> None:
    """
    Run Alembic migrations.

    Maintenance modes (inspired by CzasMuzykiAPI):
    - DB_MAINTENANCE=reset -> drop everything and run migrations from scratch
    - DB_MAINTENANCE=update (default) -> upgrade Alembic to head
    - DB_MAINTENANCE=skip -> do nothing (useful when DB is managed externally)

    Legacy toggle: RESET_DB=1 is treated the same as DB_MAINTENANCE=reset
    to keep backwards compatibility with tests/local scripts.
    """
    logger.debug("Initializing database with Alembic")
    cfg = _alembic_config()
    dialect = engine.dialect.name
    maintenance_mode = os.getenv("DB_MAINTENANCE", "update").lower()
    if os.getenv("RESET_DB", "0") == "1":
        maintenance_mode = "reset"

    if maintenance_mode not in {"reset", "update", "skip"}:
        logger.warning("Unknown DB_MAINTENANCE=%s, falling back to update", maintenance_mode)
        maintenance_mode = "update"

    try:
        if maintenance_mode == "skip":
            logger.info("DB_MAINTENANCE=skip -> skipping migrations (assuming managed externally)")
            return

        if maintenance_mode == "reset":
            logger.info("DB_MAINTENANCE=reset -> dropping all tables (including alembic_version)")
            with engine.begin() as conn:
                md = MetaData()
                md.reflect(bind=conn)
                if dialect == "sqlite":
                    conn.execute(text("PRAGMA foreign_keys=OFF"))
                    md.drop_all(bind=conn)
                    conn.execute(text("PRAGMA foreign_keys=ON"))
                else:
                    md.drop_all(bind=conn)

            command.stamp(cfg, "base")
            command.upgrade(cfg, "head")
            Base.metadata.create_all(bind=engine)
        else:
            with engine.connect() as conn:
                if not inspect(conn).has_table("alembic_version"):
                    logger.info("Stamping Alembic base (no alembic_version table found)")
                    command.stamp(cfg, "base")
            command.upgrade(cfg, "head")
            # Backfill in case migrations are incomplete
            Base.metadata.create_all(bind=engine)

        logger.info("Database maintenance mode '%s' completed successfully", maintenance_mode)
    except Exception as exc:  # pragma: no cover - only during startup
        logger.exception("Database initialization failed: %s", exc)
        raise

    logger.debug("Database ready")
