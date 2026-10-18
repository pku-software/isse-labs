#!/bin/bash
set -euo pipefail
LAB4_ROOT="$(cd "$(dirname "$0")" && pwd)"
export LAB4_ROOT
cd "$LAB4_ROOT"

case "${1:-}" in
  app)
    mkdir -p .runtime/app
    exec env CHAT_MODE=mock .venv/bin/python -u -B app.py
    ;;
  prometheus)
    mkdir -p .runtime/prometheus
    exec .tools/prometheus/prometheus \
      --config.file="$LAB4_ROOT/prometheus.yml" \
      --storage.tsdb.path="$LAB4_ROOT/.runtime/prometheus" \
      --storage.tsdb.retention.time=7d \
      --web.listen-address=127.0.0.1:9090
    ;;
  grafana)
    mkdir -p .runtime/grafana/{data,logs,plugins,dashboards}
    mkdir -p grafana/provisioning/{plugins,alerting}
    cp grafana-dashboard.json .runtime/grafana/dashboards/lab4.json
    exec .tools/grafana/bin/grafana server \
      --homepath="$LAB4_ROOT/.tools/grafana" \
      --config="$LAB4_ROOT/grafana.ini" \
      "cfg:default.paths.data=$LAB4_ROOT/.runtime/grafana/data" \
      "cfg:default.paths.logs=$LAB4_ROOT/.runtime/grafana/logs" \
      "cfg:default.paths.plugins=$LAB4_ROOT/.runtime/grafana/plugins" \
      "cfg:default.paths.provisioning=$LAB4_ROOT/grafana/provisioning"
    ;;
  *)
    printf 'Usage: bash monitoring.sh {app|prometheus|grafana}\n' >&2
    exit 2
    ;;
esac
