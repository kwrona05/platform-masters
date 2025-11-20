#!/usr/bin/env bash
set -euo pipefail

ZAP_TARGET="${ZAP_TARGET:-http://localhost:8000}"
REPORT_DIR="tests/zap/reports"
mkdir -p "${REPORT_DIR}"

docker run --rm \
  -v "$(pwd)/tests/zap:/zap/wrk:Z" \
  -t owasp/zap2docker-stable \
  zap-full-scan.py \
    -t "${ZAP_TARGET}" \
    -I \
    -m 10 \
    -J /zap/wrk/reports/zap-fullscan.json \
    -r /zap/wrk/reports/zap-fullscan.html \
    -c zap-fullscan.yaml

echo "ZAP full scan completed. Reports in ${REPORT_DIR}"
