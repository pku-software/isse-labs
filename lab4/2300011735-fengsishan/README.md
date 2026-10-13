# Lab 4：聊天应用指标

作者：冯思善，2300011735。

## 项目与运行模式

项目来自本人的 `lab3/2300011735-fengsishan/` Flask 聊天应用，保留前端和聊天记录增删改查。聊天记录保存在进程内存中，重启后清空。

默认 `CHAT_MODE=mock`：聊天返回固定测试回复，不导入或创建外部模型客户端，不读取 `.env`，不需要 Key。`GET /api/lab/status` 返回实际 mock 模式和 `external_model_calls: false`。

显式设置 `CHAT_MODE=real` 可使用原 DeepSeek 功能，Key 仅从 `DEEPSEEK_API_KEY` 环境变量取得；实验不运行此模式。real 模式的实验状态接口返回 404，mock 选项不影响真实模型调用。

## Windows PowerShell 本地运行

需要 Python 3.9 或更高版本。当前环境为 Windows x64、PowerShell 7、Python 3.12.4。在仓库根目录执行：

```powershell
Set-Location 'lab4/2300011735-fengsishan'
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force .runtime/app | Out-Null
$env:CHAT_MODE = 'mock'
$env:PORT = '5001'
& .\.venv\Scripts\python.exe -u app.py *> .runtime/app/app.log
```

应用绑定 `127.0.0.1:5001`，单进程、线程并发运行，关闭 debug 和自动重载。最后一条命令保持运行，Ctrl+C 停止。另开浏览器访问 `http://127.0.0.1:5001/`，指标地址为 `http://127.0.0.1:5001/metrics`。共享聊天记录使用锁保护；模型调用或 mock 等待期间不持有该锁。

## 聊天与模拟选项

`POST /api/messages` 接收 `message` 字符串，成功返回 HTTP 201 和包含 `id`、`message`、`reply` 的 JSON。GET 列出记录，PATCH `/api/messages/<id>` 修改消息，DELETE 同路径删除记录。

mock 模式可以接受以下非敏感测试字段，前端普通发送无需携带它们：

```json
{"message":"监控实验测试消息","mock":{"delay_seconds":0.1,"force_error":false}}
```

延迟为 0～20 秒的有限数值，默认 0.1 秒；失败标志必须为布尔值，默认 false。延迟发生在服务端处理期间。强制失败返回 HTTP 503 和 `code: simulated_error`；无效请求返回 HTTP 400。

## 指标

`metrics.py` 定义指标，通过装饰器仅记录 `POST /api/messages`。状态、静态资源、指标采集和记录查询/修改/删除不计入聊天处理次数。指标没有消息内容、姓名或请求 ID 标签。

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 完成的聊天处理累计次数；HTTP 2xx 为成功，其他响应和异常为错误，两类初始均为 0。 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数量。 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时，单位秒，包含失败请求。 |

耗时桶边界为 0.05、0.1、0.2、0.5、1、2、3、5、10、20、30 秒及自动添加的正无穷桶。`/metrics` 使用 `prometheus_client` 的标准文本格式及内容类型，暴露桶、耗时总和和次数。请求处理在 `finally` 中记录完成结果和耗时，并减少在途计数。

课程 `simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 已复制到本目录。适配器当前保持课程模板的未启用状态，尚不能发送模拟流量。

## 本地核验

当前依赖安装版本为 Flask 3.1.3、prometheus-client 0.26.0、OpenAI SDK 3.29.0。mock HTTP 核验包括一次普通成功、一次强制模拟失败、一次负延迟拒绝及两次并发的 1.2 秒慢请求，分别返回预期的 201、503、400。两次慢请求在途期间 `/metrics` 响应约 0.016 秒，观察到在途数量 2；所有请求完成后在途数量回到 0。此组核验产生成功累计 3、错误累计 2、耗时样本 5。

静态资源、状态接口及记录增删改查未增加聊天计数。另在隔离的进程内注入处理异常，确认错误计数与耗时样本仍记录、在途数量回落，并确认 mock 路径未导入模型 SDK。上述数值是单次技术核验结果；后续手动聊天和模拟都会继续累加，重启应用则重新计数。

工具包、虚拟环境和运行数据分别放在个人 `.tools/`、`.venv/` 和 `.runtime/` 内，由个人 `.gitignore` 排除；监控配置、仪表盘、结果 JSON 和截图保留为可提交文件。
