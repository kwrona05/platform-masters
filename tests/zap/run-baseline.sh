#!/usr/bin/env bash
set -euo pipefail

ZAP_TARGET="${ZAP_TARGET:-http://localhost:8000}"
REPORT_DIR="tests/zap/reports"
mkdir -p "${REPORT_DIR}"

docker run --rm \
  -v "$(pwd)/tests/zap:/zap/wrk:Z" \
  -t owasp/zap2docker-stable \
  zap-baseline.py \
    -t "${ZAP_TARGET}" \
    -I \
    -m 5 \
    -J /zap/wrk/reports/zap-baseline.json \
    -r /zap/wrk/reports/zap-baseline.html \
    -c zap-baseline.yaml

echo "ZAP baseline completed. Reports in ${REPORT_DIR}"
