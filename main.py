# main.py
from fastapi import FastAPI, Depends
from auth.router import router as auth_router  # <-- WAŻNE
from database import create_db_and_tables
from auth.utils import get_current_active_user
from models import User
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log="info",
        log_config=None
    )

# Uruchamianie aplikacji:
# uvicorn platform_masters.main:app --reload
