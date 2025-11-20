from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import config  # noqa: F401 - ensures env is loaded
from models import User
from services.admin_auth.router import router as admin_auth_router
from services.user_auth.dependencies import get_current_active_user
from services.user_auth.router import router as user_auth_router
from utils.db_maintenance import ensure_database
from utils.logger import logger

logger.info("Platform Masters API booting…")
ensure_database()

app = FastAPI(title="Platform Masters Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=600,
)

app.include_router(user_auth_router)
app.include_router(admin_auth_router)


@app.get("/protected")
def read_protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": "Dostęp uzyskany!", "user_email": current_user.email}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Zwracamy lakoniczny komunikat zamiast listy brakujących pól, by nie wyciekały szczegóły schematu
    logger.warning("Invalid request payload at %s %s", request.method, request.url.path)
    return JSONResponse(status_code=400, content={"detail": "Invalid request payload."})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log="info",
        log_config=None,
    )
