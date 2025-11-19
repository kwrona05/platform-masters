# main.py
from fastapi import FastAPI, Depends
from platform_masters.auth.router import router as auth_router  # <-- WAŻNE
from platform_masters.database import create_db_and_tables
from platform_masters.auth.utils import get_current_active_user
from platform_masters.models import User
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(title="FastAPI Auth Backend", lifespan=lifespan)

app.include_router(auth_router)  # <-- teraz działa

@app.get("/protected")
async def read_protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": "Dostęp uzyskany!", "user_email": current_user.email}

# Uruchamianie aplikacji:
# uvicorn platform_masters.main:app --reload
