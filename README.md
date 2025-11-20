# Platform Masters Auth API

Lightweight FastAPI backend z logowaniem użytkowników/adminów (JWT), resetem hasła dla adminów, migracjami Alembic oraz zestawem testów (pytest + ZAP).

## Wymagania
- Python 3.12
- Pip/virtualenv
- Opcjonalnie: Docker (do ZAP), PostgreSQL (na produkcji)

## Konfiguracja środowiska
1. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
2. Ustaw zmienne środowiskowe (przykład `.env.dev`):
   ```
   DATABASE_URL=sqlite:///./dev.db          # lokalnie; na produkcji postgres://...
   SECRET_KEY=change-me
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   CORS_ORIGINS=http://localhost:5173,https://twoj-front.app
   SMTP_HOST=...
   SMTP_PORT=587
   SMTP_USER=...
   SMTP_PASSWORD=...
   SENDER_EMAIL=...
   ```
3. Uruchom API:
   ```bash
   uvicorn main:app --reload
   ```
   Przy starcie `ensure_database()` wykona migracje Alembic do head.

## Struktura
- `main.py` – start aplikacji, CORS middleware, rejestracja routerów.
- `services/user_auth/*` – rejestracja/logowanie użytkownika, JWT.
- `services/admin_auth/*` – logowanie admina + reset hasła (pojedynczy kod w DB).
- `models/` – modele SQLAlchemy (`User`, `AdminResetCode`).
- `alembic/` – migracje (0001, 0002).
- `utils/` – logger, mailer (aiosmtplib + Jinja), db_maintenance (Alembic), szablony maili.
- `tests/` – testy jednostkowe + konfiguracja ZAP (`tests/zap`).

## Testy jednostkowe (pytest)
```bash
pytest -q
```
Fixture `conftest.py` uruchamia SQLite w `tests/.tmp/test.db`, stubuje maile i resetuje schemat per test. Dodane filtry warningów w `pytest.ini`.

## ZAP (testy bezpieczeństwa)
Wymaga Dockera. Ustaw adres aplikacji w `ZAP_TARGET` (np. `http://localhost:8000` albo preview/Render).

- Baseline (pasywny):
  ```bash
  export ZAP_TARGET="http://localhost:8000"
  ./tests/zap/run-baseline.sh
  ```
  Raporty: `tests/zap/reports/zap-baseline.html/json`.

- Full scan (spider + active):
  ```bash
  export ZAP_TARGET="http://localhost:8000"
  ./tests/zap/run-fullscan.sh
  ```
  Raporty: `tests/zap/reports/zap-fullscan.html/json`.

Konfiguracja YAML w `tests/zap/zap-baseline.yaml` i `zap-fullscan.yaml`; kontekst w `context.context`. Więcej w `tests/zap/README.md`.

## CI/CD (GitLab)
`.gitlab-ci.yml` zawiera:
- `tests` (pytest na python:3.12-slim, cache pip)
- `zap_baseline` (OWASP ZAP baseline, raporty jako artefakty; uruchamia się, gdy ustawisz `ZAP_TARGET`)

## IPv6/HTTPS/CORS
Domyślne CORS źródła pobierane z `CORS_ORIGINS` (lista rozdzielona przecinkami). Ustaw na konkretny frontend, nie zostawiaj `*` w produkcji. HTTPS zależnie od reverse proxy (Render/nginx).
