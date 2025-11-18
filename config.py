import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True
)