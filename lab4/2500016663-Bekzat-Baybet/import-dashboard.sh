#!/usr/bin/env bash
# 把个人仪表盘通过 Grafana HTTP API 导入到本机 Grafana（可重复执行，会覆盖同名仪表盘）。
# 仪表盘里引用的数据源 uid 是 provisioning 中定义的 prometheus-lab4。
set -euo pipefail
cd "$(dirname "$0")"

./.venv/Scripts/python.exe - <<'PY'
import base64
import json
import urllib.request

with open("grafana-dashboard.json", encoding="utf-8") as handle:
    dashboard = json.load(handle)
dashboard.pop("id", None)

payload = json.dumps(
    {"dashboard": dashboard, "overwrite": True, "message": "lab4 dashboard"}
).encode("utf-8")

token = base64.b64encode(b"admin:admin").decode("ascii")
request = urllib.request.Request(
    "http://127.0.0.1:3000/api/dashboards/db",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Basic {token}",
    },
)

with urllib.request.urlopen(request, timeout=15) as response:
    print(response.read().decode("utf-8"))
PY
