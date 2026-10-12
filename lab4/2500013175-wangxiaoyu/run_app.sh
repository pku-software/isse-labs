#!/bin/zsh
set -eu
cd "$(dirname "$0")"
mkdir -p .runtime/app
export MODEL_MODE="${MODEL_MODE:-mock}"
export APP_PORT="${APP_PORT:-5001}"
exec .venv/bin/python app.py
