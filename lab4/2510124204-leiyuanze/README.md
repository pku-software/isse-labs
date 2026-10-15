# Lab 4：聊天应用本地监控（Prometheus + Grafana）

在 Lab 2/3 聊天应用基础上加入 Prometheus 指标采集与 Grafana 可视化，并用课程访问脚本做本地访问模拟。
全部在本机运行，不需要 Docker、WSL 或云服务器；应用默认 mock 模式，不需要 DeepSeek Key。

## 项目来源

- 应用代码：本人 Lab 2/3 的 Flask + HTML/CSS/JavaScript 聊天应用（保留原前端、聊天 API 与 CRUD）。
- 访问调度器：课程 `lab4/starter/simulate_traffic.py` 的个人副本，未改写调度逻辑，只通过 `project_adapter.py` 适配本项目接口。
- 指标、采集配置、仪表盘、启动脚本为本 Lab 新增。

## mock 模式与 real 模式

- 默认（mock）：不创建、不调用外部模型客户端，不需要 API Key。请求仍走真实聊天接口，模拟回复、后端延迟与模拟失败都在服务端真实发生，指标在请求处理过程中产生。
- real（保留原功能）：设置环境变量 `CHAT_MODE=real` 后按原逻辑调用 DeepSeek；本实验不运行该模式，不读取 `.env`、不打印凭据。

## 指标定义

| 指标 | 类型 | 含义与记录方式 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"|"error"}` | Counter | 聊天处理完成后按结果累计一次；两种 outcome 预置为 0 |
| `chat_inprogress_requests` | Gauge | 开始处理 +1，结束（含模拟失败与异常路径）−1 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时（秒），含模拟失败；桶覆盖 0.05s～10s |

- 只统计聊天处理，不统计 `/metrics`、状态接口与静态资源。
- 不把消息内容、姓名、请求 ID 等作为标签。
- `GET /metrics` 以 Prometheus 标准文本格式暴露指标。

## 接口

| 方法与路径 | 说明 |
| --- | --- |
| `POST /api/conversations/<id>/messages` | 原聊天接口；mock 模式额外接受 `delay_seconds`（0～10，后端真实等待）与 `force_error`（返回 503 模拟失败） |
| `GET /api/status` | 返回 `{"mode": "...", "external_model_calls": ...}`，供访问脚本核验 |
| `GET /metrics` | Prometheus 指标文本 |

## 环境与版本

- Windows 10/11 x64、PowerShell 7、Python 3.9.12
- Python 包：Flask 3.1.3、prometheus-client 0.26.0、python-dotenv 1.2.1（见 `requirements.txt`）
- Prometheus 3.15.0（`windows-amd64.zip`，官方校验 SHA256 `5d333b38…b79258f87e`）
- Grafana 13.2.4（`windows-amd64.tar.gz`，官方校验 SHA256 `3e005ff5…21f4bcbd`）
- 工具解压到 `.tools/prometheus/`、`.tools/grafana/`；运行数据固定在 `.runtime/` 下（均为忽略目录，不提交）

## 从干净环境重新运行

```powershell
# 1. 依赖（首次）
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. 工具（首次）：按上表版本下载官方包，校验 SHA256 后解压为
#    .tools\prometheus\prometheus.exe
#    .tools\grafana\bin\grafana.exe

# 3. 启动三个程序（脚本内已固定配置与运行目录）
.\start-app.ps1          # 聊天应用  http://127.0.0.1:5001
.\start-prometheus.ps1   # Prometheus http://127.0.0.1:9090
.\start-grafana.ps1      # Grafana    http://127.0.0.1:3000

# 4. 访问模拟（示例）
.\.venv\Scripts\python.exe simulate_traffic.py --base-url http://127.0.0.1:5001 --output results\first-run.json
.\.venv\Scripts\python.exe simulate_traffic.py --scenario slow --slow-delay 6 --output results\changed-run.json

# 5. 结束本实验启动的进程
.\stop-lab4.ps1
```

首次启动应用时若会话存储为空，会自动创建一个会话（id=1），供访问脚本固定使用。

## 实际端口与采集配置

- 应用 `127.0.0.1:5001`；Prometheus `127.0.0.1:9090`；Grafana `127.0.0.1:3000`（匿名只读浏览，默认管理员 `admin/admin` 仅本机）。
- `prometheus.yml`：抓取 `127.0.0.1:5001/metrics`，`job_name=chat-app`，间隔 2s，超时 1s。

## 仪表盘与三个查询

仪表盘 `grafana/provisioning/dashboards/lab4-chat.json`（经 provisioning 自动加载，uid `lab4-chat-monitoring`，刷新 5s，默认时间范围最近 15 分钟）：

| Panel | PromQL | 读法 |
| --- | --- | --- |
| 成功/失败请求变化（每秒，最近 30 秒窗口） | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近窗口内平均每秒完成数，不是累计次数 |
| 正在处理的请求（当前值） | `sum(chat_inprogress_requests{job="chat-app"})` | 当前正在执行的处理数，不是在线用户数 |
| 平均处理耗时（秒，最近 30 秒窗口） | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近窗口内服务端平均耗时；无请求时可能无值 |

Histogram 暴露桶、总和与次数；本实验用总和/次数计算平均耗时。数据源通过 `grafana/provisioning/datasources/prometheus.yml` 自动注入（uid `lab4-prometheus`，指向 `http://127.0.0.1:9090`）；手动导入仪表盘时，在 Grafana 里选择该 Prometheus 数据源即可。

## 访问脚本适配

`simulate_traffic.py` 是课程调度器的个人副本，负责发送节奏与并发；三个项目相关函数在 `project_adapter.py` 中实现并已通过单请求验证，随后 `ADAPTER_READY = True`：

| 适配点 | 实现 |
| --- | --- |
| `confirm_mock_mode()` | GET `/api/status`，要求 `mode == "mock"` 且 `external_model_calls == false`，禁止重定向，失败返回 False |
| `build_chat_request()` | POST `/api/conversations/1/messages`，JSON 字段 `message`、`delay_seconds`、`force_error` |
| `response_is_success()` | HTTP 201 且 JSON 含非空字符串 `reply` 才算成功 |

运行前脚本会核验 mock 模式；非本机地址与 real 模式会被拒绝。

## 两次真实运行结果

### 第一次：完整五阶段（默认参数）

- 时间：2026-10-15 13:27:35 ～ 13:30:08（UTC），之后等待 10s 记录恢复；结果 `results/first-run.json`
- 证据：`screenshots/grafana-first-run.png`（覆盖完整模拟窗口的三 Panel）

| 阶段 | 设置 | 发送 | 成功 | 模拟失败 | 跳过 | 网络错误 | 非预期 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 1 次/秒，延迟 0.1s | 30 | 30 | 0 | 0 | 0 | 0 |
| burst | 4 次/秒，延迟 0.1s | 120 | 120 | 0 | 0 | 0 | 0 |
| slow | 2 次/秒，延迟 3s，并发 6 | 52 | 52 | 0 | 8 | 0 | 0 |
| errors | 1 次/秒，每第 3 次失败 | 30 | 20 | 10 | 0 | 0 | 0 |
| recovery | 1 次/秒，延迟 0.1s | 30 | 30 | 0 | 0 | 0 | 0 |

可复现的图表表现：success 速率在 burst 阶段升至约 4 req/s；slow 阶段平均耗时升至约 3s、在途数峰值 6、success 回落约 2 req/s（完成 52 / 跳过 8）；errors 阶段 error 曲线抬起（窗口内约 0.03 req/s）；recovery 后各曲线回到基线。阶段切换受 30s 窗口平滑影响，曲线过渡约需 30s。

### 第二次：调整参数（slow 阶段延迟 3s → 6s）

- 命令：`simulate_traffic.py --scenario slow --slow-delay 6`；时间：2026-10-15 13:39:31 ～ 13:40:05（UTC），之后等待 10s
- 结果 `results/changed-run.json`；对照 `screenshots/grafana-first-run.png`

| 指标 | 第一次 slow（3s） | 第二次 slow（6s） |
| --- | --- | --- |
| in-progress 峰值 | 6 | 6 |
| 平均处理耗时 | 2.953 s | 6.014 s |
| success 速率 | 约 2 req/s | 约 1 req/s |
| 完成 / 跳过 | 52 / 8 | 30 / 30 |

两次都通过 Prometheus 实际存储的时序核算。差异符合容量关系：吞吐 ≈ 并发上限 ÷ 处理耗时，并发上限固定 6 时，耗时翻倍使完成速率减半，其余调度机会被跳过。