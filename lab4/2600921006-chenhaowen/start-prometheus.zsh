#!/bin/zsh
set -eu
LAB4_PROJECT_DIR="${0:A:h}"
cd "$LAB4_PROJECT_DIR"
mkdir -p .runtime/prometheus
exec .tools/prometheus/prometheus \
  --config.file="$LAB4_PROJECT_DIR/prometheus.yml" \
  --storage.tsdb.path="$LAB4_PROJECT_DIR/.runtime/prometheus" \
  --web.listen-address=127.0.0.1:9090
