#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
mkdir -p "$ROOT/.runtime/app" "$ROOT/.runtime/prometheus" "$ROOT/.runtime/grafana/data" "$ROOT/.runtime/grafana/log" "$ROOT/.runtime/grafana/plugins" "$ROOT/.runtime/grafana/provisioning/datasources" "$ROOT/.runtime/grafana/provisioning/dashboards" "$ROOT/.runtime/grafana/provisioning/plugins" "$ROOT/.runtime/grafana/provisioning/alerting" "$ROOT/.runtime/grafana/dashboards"
cp "$ROOT/grafana/provisioning/datasources/prometheus.yml" "$ROOT/.runtime/grafana/provisioning/datasources/prometheus.yml"
cp "$ROOT/grafana-dashboard.json" "$ROOT/.runtime/grafana/dashboards/lab4-chat-monitoring.json"
cat > "$ROOT/.runtime/grafana/provisioning/dashboards/provider.yml" <<PROVIDER
apiVersion: 1
providers:
  - name: Lab 4
    orgId: 1
    folder: Lab 4
    type: file
    disableDeletion: true
    allowUiUpdates: true
    updateIntervalSeconds: 5
    options:
      path: $ROOT/.runtime/grafana/dashboards
PROVIDER

start_if_missing() {
  local port="$1" log_file="$2" pid_file="$3"
  shift 3
  if /usr/sbin/lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "127.0.0.1:$port already has a listener; leaving it in place."
    return
  fi
  nohup "$@" >"$log_file" 2>&1 &
  echo "$!" > "$pid_file"
  echo "Started listener on 127.0.0.1:$port (PID $!)."
}

start_if_missing 5001 "$ROOT/.runtime/app/app.log" "$ROOT/.runtime/app/app.pid" \
  /usr/bin/env CHAT_MODE=mock PORT=5001 "$ROOT/.venv/bin/python" "$ROOT/app.py"
start_if_missing 9090 "$ROOT/.runtime/prometheus/prometheus.log" "$ROOT/.runtime/prometheus/prometheus.pid" \
  "$ROOT/.tools/prometheus/prometheus" --config.file="$ROOT/prometheus.yml" --storage.tsdb.path="$ROOT/.runtime/prometheus" --web.listen-address=127.0.0.1:9090
start_if_missing 3000 "$ROOT/.runtime/grafana/grafana-stdout.log" "$ROOT/.runtime/grafana/grafana.pid" \
  /usr/bin/env GF_SERVER_HTTP_ADDR=127.0.0.1 GF_SERVER_HTTP_PORT=3000 GF_PATHS_DATA="$ROOT/.runtime/grafana/data" GF_PATHS_LOGS="$ROOT/.runtime/grafana/log" GF_PATHS_PLUGINS="$ROOT/.runtime/grafana/plugins" GF_PATHS_PROVISIONING="$ROOT/.runtime/grafana/provisioning" "$ROOT/.tools/grafana/bin/grafana" server --homepath="$ROOT/.tools/grafana" --config="$ROOT/.tools/grafana/conf/defaults.ini"
