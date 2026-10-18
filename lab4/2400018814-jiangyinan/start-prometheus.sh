#!/bin/sh
set -eu
LAB4_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$LAB4_ROOT/.runtime/prometheus"
exec "$LAB4_ROOT/.tools/prometheus/prometheus" \
  --config.file="$LAB4_ROOT/prometheus.yml" \
  --storage.tsdb.path="$LAB4_ROOT/.runtime/prometheus" \
  --web.listen-address=127.0.0.1:9090
