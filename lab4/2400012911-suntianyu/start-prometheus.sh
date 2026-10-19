#!/bin/sh
set -eu

lab4_dir=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$lab4_dir/.runtime/prometheus"

exec "$lab4_dir/.tools/prometheus/prometheus" \
  --config.file="$lab4_dir/prometheus.yml" \
  --storage.tsdb.path="$lab4_dir/.runtime/prometheus" \
  --web.listen-address=127.0.0.1:9090 \
  >> "$lab4_dir/.runtime/prometheus/prometheus.log" 2>&1
