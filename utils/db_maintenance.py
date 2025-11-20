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
    Run Alembic migrations. In dev, optional RESET_DB=1 drops all tables.
    Mirrors the maintenance pattern from CzasMuzykiAPI.
    """
    logger.debug("Initializing database with Alembic")
    cfg = _alembic_config()
    dialect = engine.dialect.name
    reset_requested = os.getenv("RESET_DB", "0") == "1"

    try:
        if reset_requested:
            logger.info("RESET_DB=1 -> dropping all tables (including alembic_version)")
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
    except Exception as exc:  # pragma: no cover - only during startup
        logger.exception("Database initialization failed: %s", exc)
        raise

    logger.debug("Database ready")
