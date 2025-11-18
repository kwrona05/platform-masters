# app/auth/router.py (Fragment)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db_session
from ..schemas import UserCreate, Token, UserLogin # Wymaga UserLogin, Token zdefiniowanych w schemas.py
from .utils import get_password_hash, verify_password, create_access_token
from ..models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db_session)):
    # 1. Weryfikacja unikalności
    existing_user = await db.get(User, user_data.email) # Użyj odpowiedniej kwerendy!
    if existing_user:
        raise HTTPException(status_code=400, detail="Email już zarejestrowany.")

    # 2. Tworzenie użytkownika
    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"message": "Rejestracja udana."}

@router.post("/login", response_model=Token)
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db_session)):
    # 1. Pobranie użytkownika
    user = await db.get(User, form_data.email) # Użyj odpowiedniej kwerendy!

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Generowanie tokenu
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}