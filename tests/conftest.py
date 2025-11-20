import os
import sys
from importlib import reload
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
import warnings

# Dodaj ścieżkę projektu na początek sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ustaw środowisko testowe zanim zaimportujemy aplikację
TEST_DB_DIR = Path(__file__).resolve().parent / ".tmp"
TEST_DB_DIR.mkdir(exist_ok=True)
TEST_DB_PATH = TEST_DB_DIR / "test.db"

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RESET_DB", "1")
os.environ.setdefault("LOG_LEVEL", "WARNING")

# Wyłącz ostrzeżenia datetime z bibliotek zewnętrznych używanych przez jose
warnings.filterwarnings("ignore", category=DeprecationWarning, module="jose.jwt")
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning:jose.jwt")

import config  # noqa: E402
import database  # noqa: E402
import main  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
from utils.db_maintenance import ensure_database  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    # Wyczyść i zainicjalizuj schemat dla sesji testowej
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ensure_database()
    yield


@pytest.fixture(scope="function")
def db_session() -> Generator:
    # Świeża baza na funkcję testową
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    # Nadpisujemy zależność DB tak, aby w każdej funkcji korzystać z jednego sesyjnego połączenia
    app = main.app

    def override_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[database.get_db_session] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def no_email(monkeypatch):
    # Stub wysyłki maili, aby testy nie robiły realnych połączeń SMTP
    monkeypatch.setattr("utils.mailer.send_reset_email_code", lambda *a, **k: None)
    monkeypatch.setattr("utils.mailer.send_reset_email_code_sync", lambda *a, **k: None)
    monkeypatch.setattr("services.admin_auth.logic.send_reset_email_code_sync", lambda *a, **k: None)
