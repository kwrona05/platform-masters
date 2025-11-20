from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db_session
from models import User
from services.user_auth import logic, schemas
from services.user_auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["User Auth"])


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db_session),
):
    return logic.register_user(db, payload)


@router.post("/login", response_model=schemas.Token)
def login_user(
    payload: schemas.UserLogin,
    db: Session = Depends(get_db_session),
):
    user = logic.authenticate_user(db, payload.email, payload.password)
    token = logic.build_access_token_for_user(user)
    return schemas.Token(access_token=token)


@router.get("/me", response_model=schemas.UserRead)
def read_me(current_user: User = Depends(get_current_active_user)):
    return current_user
