# Lab4：姜珺尚 2300015813

基于本人 Lab3 的 Flask 多会话聊天应用，保留前端、会话和消息 CRUD，以及真实模型调用功能。本实验默认使用本地 mock 回复，不需要 Key，不读取 `.env`。

## Windows PowerShell 运行

在本目录执行：

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install --index-url https://pypi.org/simple -r requirements.txt
./start-app.ps1
```

浏览器打开 `http://127.0.0.1:5001/`，新建会话后发送测试消息。应用使用单进程、多线程，监听本机 5001 端口。启动脚本显式设置 `CHAT_MODE=mock`。聊天数据存于 `.runtime/app/conversations.json`，不提交到 Git。

`CHAT_MODE` 只接受 `mock` 和 `real`，默认 `mock`。`real` 保留原 DeepSeek 请求流程，只在调用时从后端环境变量读取 `DEEPSEEK_API_KEY`；本实验不运行 real 模式。mock 不调用外部模型，前端显示当前模式。

## 接口与指标

原聊天接口仍为 `POST /api/conversations/<id>/messages`，JSON 中 `message` 为非空字符串。mock 模式可额外传入 `mock_delay_seconds`（0–30 秒有限数，默认 0.1）及 `mock_force_error`（布尔值，默认 false）。延迟发生在后端，强制失败返回 HTTP 503 和 `simulated: true`；成功保存记录并返回 HTTP 201。real 模式忽略这两个测试选项。

`GET /api/lab/status` 仅在 mock 模式返回当前模式及 `external_model_calls: false`，real 模式返回 404。`GET /api/hello` 返回连通性信息及当前模式。

`http://127.0.0.1:5001/metrics` 使用 `prometheus_client` 标准文本格式提供：

| 指标 | 含义 |
| --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | 按最终处理结果累计聊天请求数，两个标签初始化为零 |
| `chat_inprogress_requests` | 当前正在处理的聊天请求数量 |
| `chat_request_duration_seconds` | 服务端处理耗时 Histogram，包含成功和失败 |

耗时桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒及正无穷。指标装饰器覆盖原聊天 POST 处理，包括输入验证、模型回复和存储；异常时仍更新错误数、耗时并减少在途数量。创建会话、修改/删除记录、静态资源、状态和采集请求不计入聊天指标。指标不包含消息内容或请求 ID 标签，进程重启后重新计数。

数据锁只在读取和保存记录时持有，模拟等待不占有锁。原会话并发变更检查保留：如果生成回复期间会话被修改或删除，则返回 409，避免覆盖已有数据。

## 已核验的应用行为

本机使用 Python 3.14.6、Flask 3.1.3、prometheus-client 0.26.0、requests 2.34.2。Flask 测试客户端检查通过：mock 路径不调用真实模型函数，成功和模拟失败按结果累计；非法延迟和失败参数返回 400；未捕获异常仍完成指标收尾；页面、静态资源、状态、采集及 CRUD 不增加聊天请求数。real 分支仅用替身函数检查模式分流与测试参数隔离，未调用真实模型。

实际本地 HTTP 检查中，一个 2 秒慢聊天请求在处理中时，`/metrics` 约 0.018 秒返回且显示在途数为 1。请求成功后，再发送一次模拟失败请求，最终成功和错误各累计 1 次，耗时样本数为 2，在途数量回到 0。测试会话已删除，指标保留至进程重启。此检查不是课程完整五阶段模拟。

## 本地文件

`.venv/` 为 Python 虚拟环境，`.tools/` 存放后续监控工具，`.runtime/` 存放运行数据和日志，均由个人 `.gitignore` 忽略。课程 `simulate_traffic.py`、`project_adapter.py`、`prometheus.yml` 已复制到个人目录，适配器尚未启用，不能据此运行完整模拟。
