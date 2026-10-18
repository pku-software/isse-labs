#!/bin/sh
set -eu
LAB4_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export LAB4_DASHBOARDS_DIR="$LAB4_ROOT/.runtime/grafana/dashboards"
export GF_PATHS_DATA="$LAB4_ROOT/.runtime/grafana/data"
export GF_PATHS_LOGS="$LAB4_ROOT/.runtime/grafana/logs"
export GF_PATHS_PLUGINS="$LAB4_ROOT/.runtime/grafana/plugins"
export GF_PATHS_PROVISIONING="$LAB4_ROOT/provisioning"
mkdir -p "$LAB4_DASHBOARDS_DIR" "$GF_PATHS_DATA" "$GF_PATHS_LOGS" "$GF_PATHS_PLUGINS"
cp "$LAB4_ROOT/grafana-dashboard.json" "$LAB4_DASHBOARDS_DIR/lab4.json"
exec "$LAB4_ROOT/.tools/grafana/bin/grafana" server \
  --homepath="$LAB4_ROOT/.tools/grafana" \
  --config="$LAB4_ROOT/grafana.ini"
