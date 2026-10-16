#!/bin/sh
set -eu
LAB4_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export LAB4_DIR
case "${1:-}" in
  prometheus)
    mkdir -p "$LAB4_DIR/.runtime/prometheus"
    exec "$LAB4_DIR/.tools/prometheus/prometheus" \
      --config.file="$LAB4_DIR/prometheus.yml" \
      --storage.tsdb.path="$LAB4_DIR/.runtime/prometheus" \
      --web.listen-address=127.0.0.1:9090 ;;
  grafana)
    export GF_PATHS_DATA="$LAB4_DIR/.runtime/grafana/data"
    export GF_PATHS_LOGS="$LAB4_DIR/.runtime/grafana/logs"
    export GF_PATHS_PLUGINS="$LAB4_DIR/.runtime/grafana/plugins"
    export GF_PATHS_PROVISIONING="$LAB4_DIR/grafana-provisioning"
    mkdir -p "$GF_PATHS_DATA" "$GF_PATHS_LOGS" "$GF_PATHS_PLUGINS"
    # 仅本机匿名只读查看，管理员口令保存在被忽略的运行目录。
    if [ ! -f "$LAB4_DIR/.runtime/grafana/admin-password" ]; then
      (umask 077; "$LAB4_DIR/.venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(32))' > "$LAB4_DIR/.runtime/grafana/admin-password")
    fi
    GF_SECURITY_ADMIN_PASSWORD=$(cat "$LAB4_DIR/.runtime/grafana/admin-password")
    export GF_SECURITY_ADMIN_PASSWORD
    exec "$LAB4_DIR/.tools/grafana/bin/grafana" server \
      --homepath "$LAB4_DIR/.tools/grafana" --config "$LAB4_DIR/grafana.ini" ;;
  *) echo 'Usage: sh start-monitoring.sh prometheus|grafana' >&2; exit 2 ;;
esac
