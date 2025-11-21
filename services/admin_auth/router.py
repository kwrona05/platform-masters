from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db_session
from models import User
from services.admin_auth import logic, schemas
from services.admin_auth.dependencies import get_current_admin
from services.user_auth.schemas import UserRead

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post("/register", response_model=schemas.AdminRead, status_code=status.HTTP_201_CREATED)
def register_admin(
    payload: schemas.AdminCreate,
    db: Session = Depends(get_db_session),
):
    return logic.register_admin(db, payload)


@router.post("/login", response_model=schemas.Token)
def login_admin(
    payload: schemas.AdminLogin,
    db: Session = Depends(get_db_session),
):
    admin = logic.authenticate_admin(db, payload.email, payload.password)
    token = logic.build_access_token_for_admin(admin)
    return schemas.Token(access_token=token)


@router.get("/me", response_model=schemas.AdminRead)
def read_me_admin(current_admin: User = Depends(get_current_admin)):
    return current_admin


@router.post("/reset-code", status_code=status.HTTP_200_OK)
def request_reset_code(payload: schemas.ResetCodePayload, db: Session = Depends(get_db_session)):
    logic.create_reset_code(db, payload)
    return {"message": "Kod resetu został wysłany na Twój email."}


@router.post("/confirm-code", status_code=status.HTTP_200_OK)
def confirm_reset_code(payload: schemas.ConfirmCodePayload, db: Session = Depends(get_db_session)):
    logic.confirm_reset_code(db, payload)
    return {"message": "Kod jest prawidłowy."}


@router.post("/new-password", status_code=status.HTTP_200_OK)
def set_new_password(payload: schemas.NewPasswordPayload, db: Session = Depends(get_db_session)):
    logic.reset_password(db, payload)
    return {"message": "Hasło zostało zaktualizowane."}


@router.post("/users/verify", response_model=UserRead)
def verify_account(
    payload: schemas.ModerationPayload,
    db: Session = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
):
    return logic.verify_account(db, payload)


@router.post("/users/ban", response_model=UserRead)
def ban_user(
    payload: schemas.ModerationPayload,
    db: Session = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
):
    return logic.ban_user(db, payload, ban=True)


@router.post("/users/unban", response_model=UserRead)
def unban_user(
    payload: schemas.ModerationPayload,
    db: Session = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
):
    return logic.ban_user(db, payload, ban=False)
