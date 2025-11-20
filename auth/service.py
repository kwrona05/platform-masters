# app/auth/service.py (Lub zintegruj z istniejącym utils.py)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from database import get_db_session
from models import User
from utils import SECRET_KEY, ALGORITHM # Import klucza i algorytmu

# 1. Konfiguracja schematu zabezpieczeń OAuth2
# Używamy `/auth/login` jako endpointu, do którego klient musi się udać po token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Weryfikuje token JWT, dekoduje go i pobiera obiekt użytkownika z bazy.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nie udało się zweryfikować danych uwierzytelniających",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 2. Dekodowanie Tokenu
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Oczekujemy, że token ma pole 'sub' (subject), które jest emailem użytkownika
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
            
    except JWTError:
        # Jeśli token jest nieważny (np. wygasł, zły format)
        raise credentials_exception

    # 3. Pobranie użytkownika z bazy (asynchronicznie)
    # Wymaga asynchronicznej kwerendy do bazy:
    # W SQLModel/SQLAlchemy Async może wyglądać tak:
    user = await db.get(User, user_email) # Wymaga odpowiedniej kwerendy na email

    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dodatkowa weryfikacja, czy użytkownik jest aktywny.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Użytkownik nieaktywny")
    return current_user