# Lab 4：一问聊天应用的监控

基于本人 Lab 2 的 HTML/CSS/JavaScript + Flask 应用，保留聊天记录的创建、查看、修改、删除与 JSON 保存功能。新增聊天指标和本地模拟回复，用于 Prometheus 采集及 Grafana 展示。

## 本地启动

Python 3.9 或更新版本；本次使用 macOS arm64、Python 3.12.14。在个人项目目录执行：

```bash
cd /Users/carrie/isse-labs/lab4/2400018814-jiangyinan
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
LAB4_MODEL_MODE=mock .venv/bin/python app.py
```

其他电脑请替换第一行目录。浏览器打开 `http://127.0.0.1:5001/`，不要直接打开 HTML 文件。服务使用单进程、线程并发，关闭 debug/reloader，只监听本机。聊天数据写入 `.runtime/app/messages.json`，该文件不提交。停止时在启动终端按 Control+C。

## mock 与 real

`LAB4_MODEL_MODE` 默认值为 `mock`：不读取 `.env`，不请求外部模型接口，无需密钥。原聊天接口 `POST /api/messages` 仍接收 `message`，返回包含 `id`、`message`、`reply` 的记录；模拟回复会明确标注。

mock 请求还接受两个实验字段：`mock_delay` 为 0～30 秒的数字（默认 0.1），`mock_error` 为布尔值（默认 false）。等待在后端发生；强制失败等待后返回 HTTP 503 与 `simulated: true`，不会保存成功记录。无效字段返回 HTTP 400。

`GET /api/lab4/status` 在 mock 模式返回 `{"mode":"mock","external_model_calls":false}`，real 模式返回 404。

显式设置 `LAB4_MODEL_MODE=real` 时保留 Lab 2 的中转站 Responses API 调用及 `OPENAI_API_KEY`（兼容 `DEEPSEEK_API_KEY`）环境变量方式，此时才可读取本目录 `.env`。实验字段不会影响真实调用。本实验只运行 mock；不需要配置或提交真实密钥。

## 三种聊天指标

访问 `http://127.0.0.1:5001/metrics` 查看 Prometheus 标准文本格式的指标。定义位于 `metrics.py`，只包裹原 `POST /api/messages` 处理函数。

| 指标 | 含义 |
| --- | --- |
| `chat_requests_total{outcome="success"}` | 已完成且返回 2xx 的聊天请求累计数。 |
| `chat_requests_total{outcome="error"}` | 失败的聊天请求累计数，包括输入错误、模拟失败和存储异常。 |
| `chat_inprogress_requests` | 开始处理时加一，结束时减一的在途请求数。 |
| `chat_request_duration_seconds` | 服务端处理耗时，单位秒；包括输入检查、模拟等待、保存记录和失败路径。 |

Histogram 的桶上界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒及自动追加的正无穷。`_bucket{le="…"}` 是不超过该上界的累计次数，`_sum` 是总耗时，`_count` 是总次数。Counter 的两种结果启动时都初始化为零。进程重启后指标重新累计，历史数据由 Prometheus 保存。

网页、静态资源、健康/实验状态接口、查看/修改/删除记录和 `/metrics` 自身不计入聊天处理数。指标标签只包含结果类别，不包含提问内容或记录 ID。

## 运行测试

```bash
.venv/bin/python -m unittest -v test_app
```

测试使用临时聊天数据，检查模拟回复、CRUD、错误和异常后的指标收尾、参数验证、模式隔离，以及多个慢请求期间 `/metrics` 仍能及时响应。real 分支测试使用替身响应，不访问真实模型。

2026 年 10 月 18 日，七项测试全部通过。另在实际运行的 `127.0.0.1:5001` 服务上分别发送一次正常请求和一次模拟失败请求，确认 HTTP 201/503、成功和错误计数各增加一次、耗时次数为 2、Gauge 回到 0。浏览器手动发送消息也会继续增加计数；独立测试进程的指标不计入这一服务。

## 文件与运行数据

课程访问脚本的个人副本为 `simulate_traffic.py`；项目适配位于 `project_adapter.py`。采集配置为 `prometheus.yml`，目标为 `127.0.0.1:5001`，采集间隔 2 秒，超时 1 秒。

`.venv/` 存放 Python 环境；`.tools/` 用于本地监控程序；`.runtime/` 用于运行数据库和日志，均被 Git 忽略。模拟结果、仪表盘配置及截图保留为可提交文件。
