# Flask 聊天应用监控

本项目基于个人 Lab 3 的 Flask 聊天应用，保留多会话、消息增删改查和原聊天接口，增加本地 mock 回复及 Prometheus 业务指标。实验请求使用固定测试文本，不调用真实模型。

## 运行环境

已验证环境为 macOS ARM64、zsh、Python 3.12.12、uv 0.10.2；应用依赖包括 Flask 3.1.3 和 prometheus-client 0.26.0。依赖范围记录于 `requirements.txt`。

在仓库根目录执行：

```sh
cd lab4/2600921006-chenhaowen
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
CHAT_MODE=mock PORT=5001 uv run --no-project --python .venv/bin/python python app.py
```

打开 `http://127.0.0.1:5001/` 使用聊天页面，打开 `http://127.0.0.1:5001/metrics` 查看指标。应用绑定本机地址，以单进程、多线程处理请求，关闭调试和自动重载。端口由 `PORT` 配置，默认是 `5001`。

`CHAT_MODE` 默认为 `mock`，只接受 `mock` 或 `real`。mock 不创建真实模型客户端，不需要 Key；`GET /api/lab-status` 返回 `{"mode":"mock","external_model_calls":false}`。原 DeepSeek 功能保留在 real 模式中，其凭据从运行环境取得，程序不会自动读取 `.env`。本实验仅运行 mock；real 模式下实验状态接口返回 404，模拟选项不参与真实模型调用。

## 聊天接口

前端使用 `POST /api/conversations/<conversation_id>/messages`；兼容接口 `POST /api/messages` 操作 ID 为 `1` 的默认会话。两个地址经过同一个处理函数，成功返回 HTTP 201 和 `id`、`message`、`reply` 字段。

mock 请求示例：

```json
{"message":"监控实验测试消息","mock_delay_seconds":0.1,"mock_force_error":false}
```

`mock_delay_seconds` 是后端等待秒数，默认 `0.1`，范围为 `0` 至 `30` 的有限数字；`mock_force_error` 必须为布尔值，默认 `false`。强制失败在等待后返回 HTTP 503，并携带 `code: "mock_failure"`。无效模拟选项返回 HTTP 400。

存储锁只保护会话的读写，后端等待时不持有锁。mock 回复不依赖历史，允许同一会话的多个回复安全追加；real 模式仍校验生成期间的历史变化，避免把基于过期上下文的回复写入会话。

## 指标

| 指标 | 类型 | 统计范围 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 两个 POST 聊天接口完成的请求，成功和错误分别累计，初始值均为 0。 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求。 |
| `chat_request_duration_seconds` | Histogram | 聊天处理的服务端耗时，包含后端等待、存储和失败路径。 |

Histogram 桶上界为 `0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 20, 30, +Inf` 秒，同时暴露 `_sum` 和 `_count`。指标模块使用独立注册表；页面、静态资源、会话管理、消息查询和编辑、状态接口、`/metrics` 访问均不增加聊天指标。指标标签不包含消息内容、会话 ID 或用户信息。

## 本地文件

mock 聊天数据写入 `.runtime/app/mock/conversations.json`，real 数据使用独立的 `.runtime/app/real/`。日志及其他运行文件位于 `.runtime/app/`；虚拟环境位于 `.venv/`；工具目录为 `.tools/`。这些目录以及 `.env`、Python 缓存均由个人 `.gitignore` 排除。

`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 来自课程 `lab4/starter/`。调度器保留课程实现；`project_adapter.py` 是项目 HTTP 适配入口，只有完成适配并通过单请求验证后才能启用。运行结果、仪表盘配置与截图保留在可提交的位置。

## 验证

在本项目目录执行：

```sh
uv run --no-project --python .venv/bin/python python -m unittest discover -s tests -v
uv pip check --python .venv/bin/python
node --check frontend/app.js
```

HTTP 测试使用 `.runtime/app/tests/` 下的临时应用副本和随机本地端口，结束后关闭测试服务并清理测试数据。覆盖默认 mock、禁止自动读取 `.env`、指标统计范围、模拟参数校验、并发慢请求、存储失败收尾及 real 配置无法报告 mock；测试期间禁止创建外部模型客户端。
