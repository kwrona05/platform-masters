from fastapi import FastAPI
from .auth import router as auth_router
from .database import create_db_and_tables

app = FastAPI(title="FastAPI Auth Backend")

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

app.include_router(auth_router)

@app.get("/protected")
async def read_protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": "Dostęp uzyskany!", "user_email": current_user.email}

#uvicorn main:app --reload
