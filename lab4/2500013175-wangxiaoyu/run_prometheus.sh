#!/bin/zsh
set -eu
cd "$(dirname "$0")"
mkdir -p .runtime/prometheus
exec .tools/prometheus/prometheus \
  --config.file="$PWD/prometheus.yml" \
  --storage.tsdb.path="$PWD/.runtime/prometheus" \
  --web.listen-address=127.0.0.1:9090
