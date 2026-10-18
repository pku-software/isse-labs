# 本地聊天应用监控实验

应用源自本人 Lab 3 的 Flask 聊天项目，保留了原页面、`POST /api/messages` 聊天接口，以及记录的查看、修改和删除功能。本目录的记录保存在本地 `data/messages.json`，该文件不提交。

## 运行应用

在本目录中使用 Python 3.9 或更新版本：

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
LAB4_MODE=mock ./.venv/bin/python app.py
```

应用仅监听 `127.0.0.1:5001`。页面为 `http://127.0.0.1:5001/`，指标接口为 `http://127.0.0.1:5001/metrics`。默认 `mock` 模式返回固定测试回复，不读取 Key，也不调用外部模型。`GET /api/lab4/status` 仅在该模式下返回当前模式与外部模型调用状态，供课程访问脚本核验。

原有真实模型模式仍可使用：以 `LAB4_MODE=real` 启动，并在运行环境中单独配置 `DEEPSEEK_API_KEY`。本监控实验不使用真实模式，也不需要在仓库中保存 Key。

mock 模式的聊天 JSON 除 `message` 外，可选 `mock_delay_seconds`（0～8 秒）和 `mock_force_error`（布尔值）。延迟与模拟失败均在原聊天接口的后端处理过程中发生。实验消息请使用非敏感文本。

## 应用指标

| 指标 | 类型 | 记录内容 |
| --- | --- | --- |
| `chat_requests_total` | Counter | 用 `outcome` 标签区分聊天创建请求完成后的成功与错误次数 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天创建请求数 |
| `chat_request_duration_seconds` | Histogram | 每次聊天创建请求的服务端耗时，含失败请求 |

只有 `POST /api/messages` 计入以上业务指标；页面、静态资源、状态接口与 `/metrics` 不计入。指标标签不包含聊天内容。Histogram 同时提供 `_bucket`、`_sum` 和 `_count` 序列。
