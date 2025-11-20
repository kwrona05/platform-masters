# ZAP baseline (przygotowanie)

- Ustaw zmienną `ZAP_TARGET` na bazowy URL aplikacji (np. preview na GitLab/Render), np. `https://your-app.onrender.com`.
- Pipeline używa obrazu `owasp/zap2docker-stable` i uruchamia `zap-baseline.py -m 5` z raportami `zap-baseline.json/html`.
- Job jest `allow_failure: true` — możesz podnieść surowość usuwając tę flagę.
- Jeśli chcesz dodać wyjątki, przygotuj plik `zap-ignore.yml` lub parametry `-g`/`-z` zgodnie z dokumentacją ZAP.
