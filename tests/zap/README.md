# ZAP – testy bezpieczeństwa (baseline/full scan)

Struktura bazuje na automations z projektu CzasMuzykiAPI.

## Szybki baseline (passive)
```
export ZAP_TARGET="http://localhost:8000"
./tests/zap/run-baseline.sh
```
Artefakty: `tests/zap/reports/zap-baseline.html` i `.json`.

## Pełniejszy skan (spider + active)
```
export ZAP_TARGET="http://localhost:8000"
./tests/zap/run-fullscan.sh
```
Artefakty: `tests/zap/reports/zap-fullscan.html` i `.json`.

## Konfiguracja
- `tests/zap/zap-baseline.yaml` – scenariusz baseline (passive, brak aktywnego fuzzingu).
- `tests/zap/zap-fullscan.yaml` – scenariusz spider + active scan z limitami czasowymi.
- `tests/zap/context.context` – przykładowy kontekst (host/port/bez auth); dostosuj jeśli używasz JWT/cookies.

## Notatki
- Skrypty używają obrazu `owasp/zap2docker-stable`. Upewnij się, że `docker` działa lokalnie lub w CI.
- W CI ustaw `ZAP_TARGET` na adres deployu (np. preview na Render/GitLab). Domyślne `http://localhost:8000`.
- Jeśli potrzebujesz whitelist/ignore, dodaj do YAML `ignoreAlerts` lub użyj `-z "-config globalexcludeurl.url_list.url(0).regex=..."`.
