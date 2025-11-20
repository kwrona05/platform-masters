from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from models import User, UserVerificationCode
from services.user_auth.schemas import KycPayload, UserCreate, VerificationCodePayload
from utils.mailer import send_verification_email_code_sync


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_nickname(db: Session, nickname: str) -> User | None:
    return db.scalar(select(User).where(User.nickname == nickname))


def _generate_verification_code(length: int = 6) -> str:
    alphabet = "0123456789"
    from secrets import choice

    return "".join(choice(alphabet) for _ in range(length))


def _create_verification_code(db: Session, user: User) -> str:
    db.query(UserVerificationCode).filter(UserVerificationCode.user_id == user.id).delete(synchronize_session=False)
    code = _generate_verification_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    entry = UserVerificationCode(user_id=user.id, code=code, expires_at=expires_at)
    db.add(entry)
    db.commit()
    send_verification_email_code_sync(user.email, code)
    return code


def register_user(
    db: Session,
    payload: UserCreate,
    *,
    is_admin: bool = False,
    email_confirmed: bool | None = None,
    send_verification: bool = True,
) -> User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email już zarejestrowany.")
    if get_user_by_nickname(db, payload.nickname):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nick zajęty.")
    if payload.password != payload.confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hasła nie są takie same.")

    user = User(
        nickname=payload.nickname,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_admin=is_admin,
        is_email_confirmed=email_confirmed if email_confirmed is not None else False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    if send_verification and not user.is_email_confirmed:
        _create_verification_code(db, user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Konto zostało zablokowane.")
    if not user.is_email_confirmed and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Konto niepotwierdzone. Sprawdź email.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Konto jest nieaktywne.")
    return user


def build_access_token_for_user(user: User) -> str:
    return create_access_token({"sub": user.email, "is_admin": user.is_admin})


def confirm_email(db: Session, payload: VerificationCodePayload) -> None:
    user = get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie istnieje.")
    entry = (
        db.query(UserVerificationCode)
        .filter(
            UserVerificationCode.user_id == user.id,
            UserVerificationCode.code == payload.code,
            UserVerificationCode.used.is_(False),
            UserVerificationCode.expires_at > datetime.now(timezone.utc),
        )
        .order_by(UserVerificationCode.id.desc())
        .first()
    )
    if not entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kod jest nieprawidłowy lub wygasł.")

    entry.used = True
    user.is_email_confirmed = True
    db.add(entry)
    db.add(user)
    db.commit()


def resend_verification_code(db: Session, email: str) -> None:
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie istnieje.")
    if user.is_email_confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Konto już potwierdzone.")
    _create_verification_code(db, user)


def submit_kyc(db: Session, user: User, payload: KycPayload) -> User:
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Konto zostało zablokowane.")
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.bank_account = payload.bank_account
    user.billing_address = payload.billing_address
    user.pesel = payload.pesel
    user.kyc_submitted_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
