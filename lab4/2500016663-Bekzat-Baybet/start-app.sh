#!/usr/bin/env bash
# 启动聊天应用（mock 模式，不需要 DeepSeek Key）。
# 日志写入 .runtime/app/app.log，不会进入可提交的文件。
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p .runtime/app

CHAT_MODE=mock ./.venv/Scripts/python.exe app.py >> .runtime/app/app.log 2>&1
