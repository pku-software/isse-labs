#!/usr/bin/env bash
# 启动 Prometheus（仅监听本机 127.0.0.1:9090）。
# 采集配置用个人目录下的 prometheus.yml，时序数据库写入 .runtime/prometheus/，
# 因此运行数据不会进入可提交的文件。
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p .runtime/prometheus

exec .tools/prometheus/prometheus.exe \
  --config.file=prometheus.yml \
  --storage.tsdb.path=.runtime/prometheus \
  --web.listen-address=127.0.0.1:9090
