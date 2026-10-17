# Lab 4：聊天应用监控

苏英睿，2310306221。应用来自 `lab3/2310306221-suyingrui/`，保留原 HTML/CSS/JavaScript 前端与 Flask 聊天记录增删改查 API。

## 本地运行

当前环境为 macOS arm64、zsh、Python 3.9.6。在仓库根目录执行：

```sh
cd lab4/2310306221-suyingrui
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
CHAT_MODE=mock .venv/bin/python app.py --port 5001
```

页面为 <http://127.0.0.1:5001/>，指标为 <http://127.0.0.1:5001/metrics>。应用使用单进程、线程并发，无调试重载。聊天记录写入 `.runtime/app/messages.json`，共享读写有锁保护；等待模型回复时不持有存储锁。

当前安装的主要依赖版本为 Flask 3.1.3、prometheus-client 0.26.0、openai 2.48.0。

默认 `CHAT_MODE=mock`，返回固定测试回复，不导入或创建真实模型客户端，无需 Key。`GET /api/lab/status` 返回当前 mock 模式及 `external_model_calls: false`。原聊天接口为 `POST /api/messages`，请求 JSON 中的 `message` 必须为非空字符串；成功返回 HTTP 201 和包含 `id`、`message`、`reply` 的记录。

mock 模式下可附加 `mock_delay`（0～30 秒，默认 0.1 秒）和 `mock_error`（布尔值，默认 false）。等待发生在后端；强制失败在等待结束后返回 HTTP 503 和 `{"error":"Simulated model failure"}`。失败不会创建聊天记录。

`CHAT_MODE=real` 保留原 DeepSeek 调用，通过进程环境变量 `DEEPSEEK_API_KEY` 配置凭据；程序不读取 `.env`。real 模式忽略 mock 选项，实验状态接口返回 404。本实验运行使用 mock 模式。

## 指标

指标定义在 `metrics.py`，仅统计 `POST /api/messages`；状态、静态资源、指标读取和其他 CRUD 请求均不计入。

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 聊天处理完成后按结果累计，两个标签值初始化为零 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数，异常时也完成收尾 |
| `chat_request_duration_seconds` | Histogram | 从聊天处理开始到响应构造完成的服务端耗时，包含失败，单位秒 |

Histogram 桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒和正无穷。指标没有聊天正文或请求 ID 等标签。手动验证和页面聊天同样会产生真实计数。

## 回归验证

在个人目录执行 `CHAT_MODE=mock .venv/bin/python -m unittest -v test_app.py`。测试覆盖 mock 不导入模型 SDK、原 CRUD、模拟失败及未处理异常的指标收尾、保存失败回滚、非聊天访问不计数、实验选项校验和并发保存。测试使用独立的临时记录目录，不改变运行中服务的计数或聊天记录。

## 文件位置

课程 `simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 已复制到本目录。运行依赖放在 `.venv/`；监控下载包及校验文件使用 `.tools/downloads/`，工具使用 `.tools/prometheus/` 和 `.tools/grafana/`；运行数据使用 `.runtime/`。这些本地文件以及凭据均由个人 `.gitignore` 排除。结果 JSON、配置、仪表盘与截图保留为可提交文件。
