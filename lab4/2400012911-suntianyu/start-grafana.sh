#!/bin/sh
set -eu

lab4_dir=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$lab4_dir/.runtime/grafana/data" \
  "$lab4_dir/.runtime/grafana/logs" \
  "$lab4_dir/.runtime/grafana/plugins"

export GF_PATHS_DATA="$lab4_dir/.runtime/grafana/data"
export GF_PATHS_LOGS="$lab4_dir/.runtime/grafana/logs"
export GF_PATHS_PLUGINS="$lab4_dir/.runtime/grafana/plugins"
export GF_PATHS_PROVISIONING="$lab4_dir/grafana-provisioning"

exec "$lab4_dir/.tools/grafana/bin/grafana" server \
  --homepath "$lab4_dir/.tools/grafana" \
  --config "$lab4_dir/grafana.ini" \
  "cfg:default.paths.logs=$GF_PATHS_LOGS" \
  >> "$GF_PATHS_LOGS/server.stdout.log" 2>&1
