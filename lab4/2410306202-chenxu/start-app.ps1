# 启动聊天应用（Lab 4 默认 mock 模式，不调用真实模型，也不需要 Key）。
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$env:CHAT_APP_MODE = "mock"
& (Join-Path $here ".venv\Scripts\python.exe") (Join-Path $here "app.py")
