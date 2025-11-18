# app/users/router.py (Przykład)

from fastapi import APIRouter, Depends
from ..models import User
from ..auth.service import get_current_active_user # Importujemy funkcję

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Zabezpieczony endpoint: zwraca dane aktualnie zalogowanego użytkownika.
    Token JWT musi być przekazany w nagłówku Authorization: Bearer <token>
    """
    # Obiekt 'current_user' jest już instancją klasy User, pobraną z bazy danych.
    return {
        "id": current_user.id,
        "email": current_user.email,
        "auth_provider": current_user.auth_provider,
        "message": "To są twoje dane użytkownika."
    }

# Pamiętaj, aby dodać ten router do main.py:
# app.include_router(user_router)