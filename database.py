# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

# Pamiętaj, aby Render lub .env ustawiło tę zmienną
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Brak zmiennej środowiskowej DATABASE_URL.")

# Zastępuje 'postgresql://' na 'postgresql+asyncpg://' dla asynchronicznego sterownika
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Utworzenie silnika asynchronicznego
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Fabryka sesji asynchronicznej
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Klasa bazowa dla modeli
class Base(DeclarativeBase):
    pass

# Dependency Injection dla sesji DB
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()