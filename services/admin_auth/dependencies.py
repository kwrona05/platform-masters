from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.security import decode_token
from database import get_db_session
from models import User
from services.user_auth.logic import get_user_by_email

admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/auth/login")


def get_current_admin(
    token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db_session),
) -> User:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str | None = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Brak danych użytkownika w tokenie.")

    user = get_user_by_email(db, email)
    if not user or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak uprawnień administratora.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Konto administratora nieaktywne.")
    return user
