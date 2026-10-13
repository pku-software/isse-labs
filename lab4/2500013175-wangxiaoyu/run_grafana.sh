#!/bin/zsh
set -eu
cd "$(dirname "$0")"
mkdir -p .runtime/grafana/data .runtime/grafana/log .runtime/grafana/plugins .runtime/grafana/dashboards
cp grafana-dashboard.json .runtime/grafana/dashboards/chat.json
export LAB4_DASHBOARD_DIR="$PWD/.runtime/grafana/dashboards"
export GF_PATHS_DATA="$PWD/.runtime/grafana/data"
export GF_PATHS_LOGS="$PWD/.runtime/grafana/log"
export GF_PATHS_PLUGINS="$PWD/.runtime/grafana/plugins"
export GF_PATHS_PROVISIONING="$PWD/grafana/provisioning"
export GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH="$PWD/grafana-dashboard.json"
export GF_DASHBOARDS_MIN_REFRESH_INTERVAL=2s
export GF_SERVER_HTTP_ADDR=127.0.0.1
export GF_SERVER_HTTP_PORT=3000
export GF_AUTH_ANONYMOUS_ENABLED=true
export GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
export GF_ANALYTICS_REPORTING_ENABLED=false
export GF_ANALYTICS_CHECK_FOR_UPDATES=false
export GF_ANALYTICS_CHECK_FOR_PLUGIN_UPDATES=false
export GF_PLUGINS_PREINSTALL_DISABLED=true
exec .tools/grafana/bin/grafana server --homepath="$PWD/.tools/grafana"
