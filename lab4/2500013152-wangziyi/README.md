# 王子懿的 Lab 4 聊天应用监控

项目源于 `lab3/2500013152-WangZiYi`，保留聊天页面和记录的增删改查。
聊天创建接口为 `POST /api/messages`，请求 JSON 使用 `message` 字段，
成功返回 HTTP 201 和 `id`、`message`、`reply`。

## 本地运行（Windows x64 / PowerShell）

在本目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start-app.ps1
```

页面为 http://127.0.0.1:5001/，指标为 http://127.0.0.1:5001/metrics。
应用使用单进程、线程并发，只绑定本机。聊天存储使用锁保护，
数据保存到被忽略的 `.runtime/app/messages.json`。

默认 `CHAT_MODE=mock`，不创建或调用真实模型客户端，也不需要 Key。
`GET /api/lab-status` 返回实际 mock 模式和关闭外部调用的状态。
mock 聊天可附带 `mock_delay_seconds`（0–10 秒，默认 0.1 秒）与
`mock_force_error`（布尔值，默认 false）；模拟失败返回 HTTP 503。
`CHAT_MODE=real` 保留原 DeepSeek 调用，读取环境变量 `DEEPSEEK_API_KEY`，
不处理 mock 选项，实验状态接口返回 404。本实验只运行 mock。

## 业务指标

- `chat_requests_total{outcome="success"或"error"}`：聊天完成后的累计次数。
- `chat_inprogress_requests`：当前正在处理的聊天数量。
- `chat_request_duration_seconds`：服务端聊天处理耗时的 Histogram，单位秒。

指标仅覆盖 `POST /api/messages`，包括失败；异常也记录耗时并减少在途数量。
页面、状态接口、记录查询和 `/metrics` 不计入聊天指标。
指标标签不包含消息内容或用户身份。

课程 `simulate_traffic.py` 与待适配的 `project_adapter.py` 已复制到本目录。
