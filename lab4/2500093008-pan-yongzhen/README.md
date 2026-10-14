# 潘勇圳的聊天应用监控实验

学号：2500093008。应用源自个人 Lab 3 Flask 聊天项目，保留前端、多会话及消息增删改查。

## 本地启动

本次环境为 macOS arm64、zsh、Python 3.12。以下命令在个人 Fork 的仓库根目录执行：

```sh
python3 -m venv lab4/2500093008-pan-yongzhen/.venv
lab4/2500093008-pan-yongzhen/.venv/bin/python -m pip install -r lab4/2500093008-pan-yongzhen/requirements.txt
MODEL_MODE=mock PORT=5001 lab4/2500093008-pan-yongzhen/.venv/bin/python lab4/2500093008-pan-yongzhen/app.py
```

应用仅监听 127.0.0.1，默认地址 http://127.0.0.1:5001/ ，单进程、多线程。会话保存在个人 `.runtime/app/conversations.json`，不提交 Git。

## 模型模式与请求

默认 `MODEL_MODE=mock`，无需 Key，不调用外部模型。`GET /api/lab/status` 返回实际 mock 状态和 `external_model_calls: false`。显式设置 `MODEL_MODE=real` 才启用原 DeepSeek 调用，所需 Key 从环境变量读取；real 模式的实验状态接口返回 404，忽略模拟选项。本实验仅使用 mock，不读取 `.env`。

前端使用 `POST /api/conversations/<id>/messages`；兼容接口 `POST /api/messages` 使用默认会话。JSON 的 `message` 为消息文本。mock 模式额外支持 `mock_delay_seconds`（0–10 秒，默认 0.1）和 `mock_force_error`（布尔值，默认 false）。成功返回 201 与 `id/message/reply`，模拟失败返回 503 与错误 JSON。延迟期间不持有存储锁。

## 应用指标

`GET /metrics` 使用 Prometheus 标准文本格式。两个聊天 POST 入口均被统计，包括参数错误与异常；页面、CRUD、状态接口及采集请求不计入聊天数量。

- `chat_requests_total{outcome="success"或"error"}`：完成的聊天处理累计次数，两种结果初始化为零。
- `chat_inprogress_requests`：正在处理的聊天请求数量，异常也会减回。
- `chat_request_duration_seconds`：服务端聊天处理耗时，包含失败；桶上界为 0.05、0.1、0.25、0.5、1、2、3、5、10、15 秒及 +Inf。

指标定义位于 `metrics.py`。开发验证请求也会计入指标，服务进程重启后内存指标重新开始。
