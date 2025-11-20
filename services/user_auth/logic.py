from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from models import User
from services.user_auth.schemas import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, payload: UserCreate, *, is_admin: bool = False) -> User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email już zarejestrowany.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Konto jest nieaktywne.")
    return user


def build_access_token_for_user(user: User) -> str:
    return create_access_token({"sub": user.email, "is_admin": user.is_admin})
