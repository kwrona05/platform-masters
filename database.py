# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()
# Pamiętaj, aby Render lub .env ustawiło tę zmienną
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Brak zmiennej środowiskowej DATABASE_URL.")

if DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    raise ValueError("DATABASE_URL musi zaczynać się od postgres:// lub postgresql://")

print("Async database URL:", ASYNC_DATABASE_URL)



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

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)