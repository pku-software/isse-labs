#!/bin/zsh
set -eu
export LAB4_PROJECT_DIR="${0:A:h}"
cd "$LAB4_PROJECT_DIR"
mkdir -p .runtime/grafana/{data,logs,plugins}
mkdir -p grafana/provisioning/{plugins,alerting}
exec .tools/grafana/bin/grafana server \
  --homepath "$LAB4_PROJECT_DIR/.tools/grafana" \
  --config "$LAB4_PROJECT_DIR/grafana.ini"
