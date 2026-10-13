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

课程 `simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 已复制到本目录。调度器保持课程原件不变；个人适配器已完成 HTTP 核验并启用。

## 本地核验

当前依赖安装版本为 Flask 3.1.3、prometheus-client 0.26.0、OpenAI SDK 3.29.0。mock HTTP 核验包括一次普通成功、一次强制模拟失败、一次负延迟拒绝及两次并发的 1.2 秒慢请求，分别返回预期的 201、503、400。两次慢请求在途期间 `/metrics` 响应约 0.016 秒，观察到在途数量 2；所有请求完成后在途数量回到 0。此组核验产生成功累计 3、错误累计 2、耗时样本 5。

静态资源、状态接口及记录增删改查未增加聊天计数。另在隔离的进程内注入处理异常，确认错误计数与耗时样本仍记录、在途数量回落，并确认 mock 路径未导入模型 SDK。上述数值是单次技术核验结果；后续手动聊天和模拟都会继续累加，重启应用则重新计数。

工具包、虚拟环境和运行数据分别放在个人 `.tools/`、`.venv/` 和 `.runtime/` 内，由个人 `.gitignore` 排除；监控配置、仪表盘、结果 JSON 和截图保留为可提交文件。

## 本地监控工具与配置

本项目使用 Windows amd64 的官方稳定程序：[Prometheus 3.15.0](https://prometheus.io/download/) 和 [Grafana OSS 13.2.3](https://grafana.com/grafana/download/13.2.3?edition=oss&platform=windows)，不用 Docker、WSL 或云服务器。

从干净环境创建上述虚拟环境后，在个人目录执行：

```powershell
& .\.venv\Scripts\python.exe .\install-tools.py
& .\start-monitoring.ps1
```

`install-tools.py` 在下载前检查实际路径的 Git 忽略规则及未跟踪状态，从官方地址分段下载固定版本、支持续传，并通过官方 SHA256 整包校验后解压。下载包、分段和校验文件在 `.tools/downloads/`；工具直接解压到 `.tools/prometheus/`、`.tools/grafana/`。首次安装需要联网，工具程序不提交。

| 下载包 | 官方 SHA256 |
| --- | --- |
| `prometheus-3.15.0.windows-amd64.zip` | `5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e` |
| `grafana_13.2.3_36482603486_windows_amd64.tar.gz` | `dafe883a7c15543c6d6710b868eb8b4053353441ce7ceacf150942b8de3960f0` |

启动脚本再次检查忽略规则，在可用端口启动隐藏的本地进程，保留进程号到 `.runtime/monitoring-processes.json`。端口被占用时停止启动并报错，不关闭已有服务。应用单独按前面的命令启动。

Prometheus 的实际命令相当于以下 PowerShell 命令（在个人目录内执行）：

```powershell
& .\.tools\prometheus\prometheus.exe --config.file=prometheus.yml --storage.tsdb.path=.runtime/prometheus --web.listen-address=127.0.0.1:9090 --storage.tsdb.retention.time=7d
```

`prometheus.yml` 每 2 秒采集 `127.0.0.1:5001/metrics`，超时 1 秒，job 为 `chat-app`。数据库在 `.runtime/prometheus/`。浏览器访问 `http://127.0.0.1:9090/targets`。

Grafana 的实际启动参数为 `--homepath="<个人目录>/.tools/grafana" --config="<个人目录>/grafana.ini"`；若使用 `grafana.exe` 而非兼容入口 `grafana-server.exe`，参数前增加 `server`。启动脚本给子进程显式设置：

| 环境变量 | 个人目录下的实际位置 |
| --- | --- |
| `GF_PATHS_DATA` | `.runtime/grafana/data/` |
| `GF_PATHS_LOGS` | `.runtime/grafana/log/` |
| `GF_PATHS_PLUGINS` | `.runtime/grafana/plugins/` |
| `GF_PATHS_PROVISIONING` | `provisioning/` |
| `LAB4_DASHBOARD_DIR` | `.runtime/grafana/dashboards/` |

Grafana 只监听 `127.0.0.1:3000`，允许匿名 Viewer 在本机查看。数据源由 `provisioning/datasources/prometheus.yml` 配置，名称 `Lab4 Prometheus`、UID `lab4-prometheus`、地址 `http://127.0.0.1:9090`。配置禁用更新检查、遥测及预装插件下载。

`start-monitoring.ps1` 将个人 `grafana-dashboard.json` 复制到被忽略的运行目录，由 `provisioning/dashboards/lab4.yml` 加载。仪表盘地址为 `http://127.0.0.1:3000/d/lab4-chat-2300011735`，时区按浏览器显示，刷新间隔 2 秒。在其他 Grafana 实例导入此 JSON 前，创建 UID 为 `lab4-prometheus` 的 Prometheus 数据源，或将三个 Panel 和查询的数据源 UID 改成该实例已有数据源的 UID。

| Panel | PromQL | 含义 |
| --- | --- | --- |
| 成功 / 失败请求完成速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒窗口内平均每秒完成次数，按结果分为两条曲线。 |
| 正在处理的聊天请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 采集瞬间正在处理的数量，不是在线用户数。 |
| 平均服务端处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 同一窗口内耗时总和增速除以次数增速，单位秒，包含失败处理。 |

`UP` 表示最近一次采集成功。开始采集前的聊天没有历史采样点；`rate` 至少需要两个样本，没有新聊天的窗口内平均耗时可能无值。仪表盘保留这些无值，不补成零。Histogram 的 `le` 桶表示耗时不超过该边界的累计次数，`+Inf` 桶包含全部样本。

本地 HTTP 核验确认 `chat-app` Target 为 `UP`，实际目标为 `http://127.0.0.1:5001/metrics`，采集间隔 2 秒、超时 1 秒。Grafana 13.2.3 的数据库健康状态为 `ok`，三个实际 Panel 查询均返回 HTTP 200，数据源代理查询 `up{job="chat-app"}` 得到 1。核验时聊天累计为成功 5、错误 2；最近窗口无新聊天，请求速率和在途数为 0，平均耗时为 `NaN`。完整访问模拟的结果另由真实脚本执行生成。

## 课程访问脚本适配

`project_adapter.py` 的 `confirm_mock_mode()` 对本机 `/api/lab/status` 做实际 GET，要求 HTTP 200、`mode` 为 `mock` 且 `external_model_calls` 为布尔值 false，禁用代理和重定向。`build_chat_request()` 构造原 `POST /api/messages` 请求，包含 `message` 及 `mock.delay_seconds`、`mock.force_error`。`response_is_success()` 要求 HTTP 201 和合法的 `id`、非空 `message`、非空 `reply`，拒绝错误或无效响应。适配器和调度器均保留本机地址限制，不携带 Key、不打印聊天正文。

单请求实际核验得到正常 201 和强制失败 503，并正确识别结果。另将同一应用的实验状态接口以 real 配置运行于临时本机端口；调度器在状态核验阶段以退出码 2 拒绝，向该服务发送聊天请求数为 0，未导入模型客户端。核验通过后设置 `ADAPTER_READY=True`。

完整运行时，在个人目录用虚拟环境 Python 调用 `simulate_traffic.py`，`--base-url` 使用应用地址 `http://127.0.0.1:5001`，首次结果指定为 `results/first-run.json`，修改参数后的结果指定为 `results/changed-run.json`。脚本默认五阶段各 30 秒、并发上限 6、末尾等待 10 秒；阶段末尾还等待在途请求收尾。脚本只发送 HTTP 请求，指标由应用产生；客户端平均耗时包含网络开销，与服务端 Histogram 分开报告。

## 两次实际模拟结果

以下时间均为北京时间，日期为 2026-10-13；结果 JSON 中的时间为 UTC。两次运行均使用本地 mock，退出码为 0，没有中断、网络错误或非预期结果。首次运行命令为：

```powershell
& .\.venv\Scripts\python.exe -u .\simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
```

每阶段的发送窗口为 30 秒；慢请求收尾会延长实际阶段时间，并发上限为 6，单请求超时 10 秒，最终采集等待 10 秒。

| 阶段 | 实际起止时间 | 目标频率（次/秒） | 后端延迟（秒） | 实际发送 | 成功 | 模拟失败 | 跳过 | 客户端平均耗时（秒） |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 16:39:30–16:40:00 | 1 | 0.1 | 30 | 30 | 0 | 0 | 0.1328 |
| burst | 16:40:00–16:40:30 | 4 | 0.1 | 120 | 120 | 0 | 0 | 0.1338 |
| slow | 16:40:30–16:41:03 | 2 | 3 | 52 | 52 | 0 | 8 | 3.0318 |
| errors | 16:41:03–16:41:33 | 1 | 0.1 | 30 | 20 | 10 | 0 | 0.1306 |
| recovery | 16:41:33–16:42:03 | 1 | 0.1 | 30 | 30 | 0 | 0 | 0.1330 |

`errors` 阶段每第 3 次请求强制失败。首次共计划 270 次发送机会，实际发送 262 次，成功 252 次、预期模拟失败 10 次、跳过 8 次。原始结果为 [results/first-run.json](results/first-run.json)。

首次仪表盘的截图范围为 16:39:15–16:43:05，覆盖全部阶段及恢复后的采集。实际图表中 burst 成功速率升高，slow 在途数量约 5～6、服务端平均耗时接近 3 秒，errors 出现错误速率，随后回落。Prometheus 在首次完整区间采到的在途最大值为 6、服务端窗口平均耗时最大值约 3.0006 秒。原始图片为 [screenshots/grafana-dashboard.png](screenshots/grafana-dashboard.png)；采集目标图片为 [screenshots/prometheus-targets.png](screenshots/prometheus-targets.png)。

第二次只运行 slow，唯一修改的场景参数为 `--slow-delay 6`，其他参数保持默认：

```powershell
& .\.venv\Scripts\python.exe -u .\simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --slow-delay 6 --output results/changed-run.json
```

第二次的实际起止为 16:53:40–16:54:15，发送窗口仍为 30 秒、目标频率 2 次/秒、并发上限 6。原始结果为 [results/changed-run.json](results/changed-run.json)，首次文件保持不变。

| slow 对比 | 首次 | 第二次 |
| --- | ---: | ---: |
| 后端延迟（秒） | 3 | 6 |
| 计划发送机会 | 60 | 60 |
| 实际发送 / 成功 | 52 / 52 | 30 / 30 |
| 跳过发送机会 | 8 | 30 |
| 客户端平均耗时（秒，含网络开销） | 3.0318 | 6.0300 |
| 采集到的在途最大值 | 6 | 6 |
| 服务端窗口平均耗时最大值（秒） | 约 3.0006 | 约 6.0008 |

第二次服务端耗时接近 6 秒，而在途数量仍受并发上限 6 限制。占用时间加倍后，稳定处理能力约为每秒 1 次，低于每秒 2 次的发送目标，跳过次数增加。该区间查询到的成功完成速率最大值约 0.9643 次/秒；它是 30 秒窗口的采集估计值，不等于目标频率或有限阶段的总次数除以发送时间。

30 秒窗口会混合窗口内已完成请求，使阶段边界平滑，但不保证每次曲线都逐渐上升。第二次运行前窗口内没有新请求，平均耗时为 `NaN`；16:53:46 仍无值，16:53:48 首个有值的采样点约为 6.0006 秒。Histogram 在处理结束时记录耗时，此时新样本均为约 6 秒的请求，没有之前的短请求混入窗口。

采集间隔为 2 秒，0.1 秒的短请求可能在两次采集之间完成，因此在途曲线可能漏掉短峰值。脚本达到并发上限时跳过发送机会，不无限排队；目标发送频率、实际发送频率和图上的窗口完成速率应分开理解。

复现时先启动 mock 应用及监控程序，等待 Target 为 UP，再运行上述命令。若要保留仓库中的两份原始结果，可将复现输出改为 `results/replay-first.json`、`results/replay-changed.json`。Grafana 选择新运行的实际时间区间；原始截图和已保存的结果不会随复现自动更新。运行数据库被忽略，干净环境不会附带本次历史时间序列。`grafana-dashboard.json` 已从实际 Grafana 导出，保留三个 Panel 的数据源引用并去掉实例数据库 ID。
