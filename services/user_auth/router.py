from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db_session
from models import User
from services.user_auth import logic, schemas
from services.user_auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["User Auth"])


@router.post("/register", response_model=schemas.RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db_session),
):
    logic.register_user(db, payload)
    return {"message": "Kod weryfikacyjny został wysłany na podany email."}


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


@router.post("/verify-code", status_code=status.HTTP_200_OK)
def confirm_email(payload: schemas.VerificationCodePayload, db: Session = Depends(get_db_session)):
    logic.confirm_email(db, payload)
    return {"message": "Konto potwierdzone. Możesz się zalogować."}


@router.post("/resend-code", status_code=status.HTTP_200_OK)
def resend_verification(payload: schemas.ResendVerificationPayload, db: Session = Depends(get_db_session)):
    logic.resend_verification_code(db, payload.email)
    return {"message": "Kod został wysłany ponownie."}


@router.post("/kyc", response_model=schemas.UserRead)
def submit_kyc(
    payload: schemas.KycPayload,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session),
):
    return logic.submit_kyc(db, current_user, payload)
