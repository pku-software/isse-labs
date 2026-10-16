#!/bin/zsh
set -eu
cd "$(dirname "$0")"
case "${1:-}" in
  prometheus)
    mkdir -p .runtime/prometheus
    exec .tools/prometheus/prometheus --config.file=prometheus.yml --storage.tsdb.path=.runtime/prometheus --web.listen-address=127.0.0.1:9090
    ;;
  grafana)
    mkdir -p .runtime/grafana/{data,log,plugins,dashboards}
    cp grafana-dashboard.json .runtime/grafana/dashboards/
    export LAB4_DASHBOARD_DIR="$PWD/.runtime/grafana/dashboards"
    export GF_PATHS_DATA="$PWD/.runtime/grafana/data"
    export GF_PATHS_LOGS="$PWD/.runtime/grafana/log"
    export GF_PATHS_PLUGINS="$PWD/.runtime/grafana/plugins"
    export GF_PATHS_PROVISIONING="$PWD/grafana-provisioning"
    exec .tools/grafana/bin/grafana server --homepath "$PWD/.tools/grafana" --config "$PWD/grafana.ini"
    ;;
  *)
    echo 'Usage: zsh start-monitoring.sh prometheus|grafana' >&2
    exit 2
    ;;
esac
