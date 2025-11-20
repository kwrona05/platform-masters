from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
import secrets

from core.security import create_access_token, hash_password
from models import AdminResetCode, User
from services.admin_auth.schemas import AdminCreate, ConfirmCodePayload, NewPasswordPayload, ResetCodePayload
from services.user_auth.logic import authenticate_user, get_user_by_email, register_user
from services.user_auth.schemas import UserCreate
from utils.mailer import send_reset_email_code_sync


def register_admin(db: Session, payload: AdminCreate) -> User:
    user_payload = UserCreate(email=payload.email, password=payload.password)
    return register_user(db, user_payload, is_admin=True)


def authenticate_admin(db: Session, email: str, password: str) -> User:
    user = authenticate_user(db, email, password)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień administratora.",
        )
    return user


def build_access_token_for_admin(user: User) -> str:
    return create_access_token({"sub": user.email, "is_admin": True})


def _generate_reset_code(length: int = 6) -> str:
    alphabet = "0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_reset_code(db: Session, payload: ResetCodePayload) -> str:
    admin = get_user_by_email(db, payload.email)
    if not admin or not admin.is_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin nie istnieje.")

    # Usuń wcześniejsze kody dla tego admina, żeby nie gromadzić starych wpisów
    db.query(AdminResetCode).filter(AdminResetCode.user_id == admin.id).delete(synchronize_session=False)

    code = _generate_reset_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    reset_entry = AdminResetCode(user_id=admin.id, code=code, expires_at=expires_at)
    db.add(reset_entry)
    db.commit()
    send_reset_email_code_sync(payload.email, code)
    return code


def _get_valid_reset_code(db: Session, email: str, code: str) -> AdminResetCode:
    admin = get_user_by_email(db, email)
    if not admin or not admin.is_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin nie istnieje.")

    entry = (
        db.query(AdminResetCode)
        .filter(
            AdminResetCode.user_id == admin.id,
            AdminResetCode.code == code,
            AdminResetCode.used.is_(False),
            AdminResetCode.expires_at > datetime.now(timezone.utc),
        )
        .order_by(AdminResetCode.id.desc())
        .first()
    )
    if not entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kod jest nieprawidłowy lub wygasł.")
    return entry


def confirm_reset_code(db: Session, payload: ConfirmCodePayload) -> None:
    _get_valid_reset_code(db, payload.email, payload.code)


def reset_password(db: Session, payload: NewPasswordPayload) -> None:
    if payload.password != payload.confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hasła nie są takie same.")

    entry = _get_valid_reset_code(db, payload.email, payload.code)
    admin = get_user_by_email(db, payload.email)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin nie istnieje.")

    admin.hashed_password = hash_password(payload.password)
    entry.used = True
    db.add(admin)
    db.add(entry)
    db.commit()
