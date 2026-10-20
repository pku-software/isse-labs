#!/usr/bin/env bash
# 启动 Grafana（仅监听本机 127.0.0.1:3000）。
# 数据、日志、插件全部指向 .runtime/grafana/ 下的子目录，
# 数据源由 provisioning/ 自动加载，避免默认路径把数据库写进可提交目录。
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

export GF_PATHS_DATA="$ROOT/.runtime/grafana/data"
export GF_PATHS_LOGS="$ROOT/.runtime/grafana/logs"
export GF_PATHS_PLUGINS="$ROOT/.runtime/grafana/plugins"
export GF_PATHS_PROVISIONING="$ROOT/provisioning"

# 仅本机访问；管理员口令是本地实验用的默认值，只在这台机器上有意义。
export GF_SERVER_HTTP_ADDR=127.0.0.1
export GF_SERVER_HTTP_PORT=3000
export GF_SECURITY_ADMIN_USER=admin
export GF_SECURITY_ADMIN_PASSWORD=admin

mkdir -p "$GF_PATHS_DATA" "$GF_PATHS_LOGS" "$GF_PATHS_PLUGINS"

exec .tools/grafana/bin/grafana.exe server --homepath "$ROOT/.tools/grafana"
