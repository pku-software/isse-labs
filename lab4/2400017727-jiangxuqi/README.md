# 聊天应用本地监控

基于 Lab 3 `2400017727-JiangXuqi` 的 Flask 应用，保留聊天记录的创建、查看、修改和删除。

## 运行应用

在本目录创建 `.venv` 并安装 `requirements.txt`，然后执行：

```bash
MODEL_MODE=mock .venv/bin/python app.py
```

默认地址为 http://127.0.0.1:5001，可用 `PORT` 修改端口。单进程、线程并发运行，聊天记录仅存在内存中。

默认 `MODEL_MODE=mock`，不调用外部模型、不读取 `.env`。`MODEL_MODE=real` 保留原 DeepSeek 功能，凭据仅从进程环境 `DEEPSEEK_API_KEY` 获取；本实验使用 mock。

## 接口

- `POST /api/messages`：JSON `{"message":"测试消息"}`，成功返回 201 和 `id`、`message`、`reply`。
- mock 可追加 `"mock":{"delay_seconds":3,"force_error":false}`，延迟允许 0–10 秒；强制失败返回 503。
- `GET /api/messages`、`PATCH /api/messages/<id>`、`DELETE /api/messages/<id>`：聊天记录增删改查。
- `GET /api/lab-status`：返回实际运行模式与外部模型调用是否启用。
- `GET /metrics`：Prometheus 文本格式指标。

## 指标

仅 `POST /api/messages` 计入聊天业务指标，包括失败请求。消息正文与记录 ID 不作为标签。

| 指标 | 含义 |
| --- | --- |
| `chat_requests_total{outcome="success或error"}` | 已完成聊天请求累计次数 |
| `chat_inprogress_requests` | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | 服务端聊天耗时 Histogram，单位秒，包含失败请求 |

工具包位于 `.tools/`，运行数据位于 `.runtime/`，虚拟环境位于 `.venv/`，均由个人忽略规则排除。
