# Lab 4：聊天应用监控（Prometheus + Grafana）

本目录是 Lab 2/3 那个 Flask 聊天应用的 Lab 4 副本：前端、聊天 API 与 CRUD 都保持原样，
新增了 Prometheus 指标、本地模拟（mock）模式、以及课程访问脚本的项目适配部分。

## 运行模式：mock 与 real

- 不设置 `CHAT_APP_MODE` 时默认是 **mock**：用固定测试回复代替真实模型调用，不创建也不调用
  任何外部模型客户端，因此不需要 API Key，也不产生模型调用费用。请求仍然真实经过
  应用的聊天处理逻辑，指标就是在那里产生的。
- 设置 `CHAT_APP_MODE=real` 才走真实的 DeepSeek 调用；Key 只在后端从 `DEEPSEEK_API_KEY`
  环境变量读取，不进入前端、镜像、日志、指标标签或提交内容。
- `GET /api/status` 如实报告当前进程的模式，例如 `{"mode":"mock","external_model_calls":false}`，
  访问脚本用它来确认服务处于 mock 模式。

## 指标定义（`metrics.py`）

| 类型 | 名称 | 记录方式 |
| --- | --- | --- |
| Counter | `chat_requests_total{outcome="success"|"error"}` | 聊天处理结束后按结果累计一次，两种 outcome 都预先初始化为 0 |
| Gauge | `chat_inprogress_requests` | 开始处理时加一，结束时减一；成功和异常路径都会回落 |
| Histogram | `chat_request_duration_seconds` | 记录每次聊天处理的服务端耗时，桶覆盖 0.05 秒到 10 秒 |

`GET /metrics` 用 `prometheus_client` 的标准文本格式输出。`/metrics` 自身、`/api/status`
和静态资源的访问都不计入聊天指标，也不把消息内容等放进标签。
会话存储由可重入锁保护；应用以单进程多线程运行，慢请求处理期间 `/metrics` 仍可被采集。

## 实际端口

| 程序 | 地址 |
| --- | --- |
| 聊天应用 | http://127.0.0.1:5001 |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |

Grafana 是本机实验实例（`admin` / `admin`，只在 127.0.0.1 监听），不要用于任何真实环境。

## 工具版本与启动方法（Windows / PowerShell）

工具版本：Prometheus `3.15.0`（windows-amd64）、Grafana `13.2.4`（windows-amd64）。
下载包与校验文件放在 `.tools/downloads/`，解压目录为 `.tools/prometheus/` 与 `.tools/grafana/`；
运行数据写到 `.runtime/prometheus/`、`.runtime/grafana/`，应用日志写到 `.runtime/app/`。
`.tools/`、`.runtime/`、`.venv/`、`data/` 都在本目录 `.gitignore` 中，不进入提交。

从干净环境重新运行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start-app.ps1          # 聊天应用，mock 模式，127.0.0.1:5001
.\start-prometheus.ps1   # 采集 .runtime/prometheus，127.0.0.1:9090
.\start-grafana.ps1      # 数据写到 .runtime/grafana，127.0.0.1:3000
.\import-dashboard.ps1   # 导入个人仪表盘
```

`prometheus.yml` 的采集间隔 2 秒、超时 1 秒，目标为 `127.0.0.1:5001`，作业名 `chat-app`。
Grafana 的数据源由 `provisioning/datasources/prometheus.yml` 自动导入（uid `lab4-prometheus`，
指向 `http://127.0.0.1:9090`）；仪表盘 `grafana-dashboard.json` 用 `import-dashboard.ps1`
通过 HTTP API 导入，再次运行会覆盖更新同一份仪表盘。

## 三个 Panel 的查询与含义

| Panel | PromQL | 看什么 |
| --- | --- | --- |
| 成功/失败请求变化 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒窗口内平均每秒**完成**的请求数，不是累计次数 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前正在执行的聊天处理数量（瞬时值），不是在线用户数 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近窗口内服务端平均处理耗时（秒），由 Histogram 的总和除以次数得到 |

窗口是 `[30s]`，所以每个瞬间的读数都是最近 30 秒的平均：阶段中点的读数会混有上一阶段的流量，
阶段末尾才接近该阶段的真实水平。

## 访问脚本的适配位置（`project_adapter.py`）

`simulate_traffic.py` 是课程调度脚本的个人副本，负责发送节奏与有限并发，未作改动。
项目相关部分都在 `project_adapter.py` 中实现：

| 适配点 | 本项目实现 |
| --- | --- |
| `confirm_mock_mode` | `GET /api/status`，只有 `mode=mock` 且 `external_model_calls=false` 才返回 True，不跟随重定向 |
| `build_chat_request` | `POST /api/messages`（应用原有聊天接口），请求体 `{"message", "delay_seconds", "force_error"}` |
| `response_is_success` | HTTP 201 且返回记录含非空 `reply` 才算成功；模拟失败为 503 与错误 JSON |

模拟延迟在后端处理期间发生，不在客户端 sleep；`delay_seconds` 在 mock 模式下被限制在 0～10 秒，
`real` 模式一律忽略这两个选项。

单请求验证：mock 服务核验为 True，`CHAT_APP_MODE=real` 的实例核验为 False 且脚本拒绝运行（退出码 2）；
一次正常请求成功、一次强制失败被识别为预期失败、一次 2 秒慢请求实测耗时 2.02 秒。

## 两次真实模拟运行

两次运行都在本机完成，应用为 mock 模式，脚本只发出非敏感测试消息。

### 第一次：默认参数，五个阶段完整运行

命令：`.\.venv\Scripts\python.exe simulate_traffic.py --output results\first-run.json`

运行时间：2026-10-17 15:59:07 ～ 16:01:40（本地时间，UTC+8），结果见 `results/first-run.json`。

| 阶段 | 时间 | 发送 | 成功 | 失败 | 跳过 | 设置 |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 15:59:07–15:59:37 | 30 | 30 | 0 | 0 | 1 次/秒，延迟 0.1 秒 |
| burst | 15:59:37–16:00:07 | 120 | 120 | 0 | 0 | 4 次/秒，延迟 0.1 秒 |
| slow | 16:00:07–16:00:40 | 52 | 52 | 0 | 8 | 2 次/秒，延迟 3 秒，并发上限 6 |
| errors | 16:00:40–16:01:10 | 30 | 20 | 10 | 0 | 1 次/秒，每第 3 个请求失败 |
| recovery | 16:01:10–16:01:40 | 30 | 30 | 0 | 0 | 1 次/秒，延迟 0.1 秒 |

退出码 0，没有网络错误和非预期结果。`slow` 阶段实际持续 33 秒，因为阶段结束时仍有 3 秒的
在途请求；`跳过 8` 是在途数已占满 6 个并发上限时的调度放弃，所以目标速率高于完成速率。

阶段末段从 Prometheus 读到的数值：burst 成功约 3.82 次/秒；slow 平均耗时 3.0 秒、
在途峰值 6；errors 成功约 0.79 次/秒、失败约 0.29 次/秒；recovery 平均耗时回到 0.1 秒。

### 第二次：只改一个参数（`--burst-rate 8`）

命令：`.\.venv\Scripts\python.exe simulate_traffic.py --scenario burst --burst-rate 8 --output results\changed-run.json`

运行时间：2026-10-17 16:08:12 ～ 16:08:42（本地时间），结果见 `results/changed-run.json`。

| 指标 | 第一次 burst（4 次/秒） | 第二次 burst（8 次/秒） |
| --- | --- | --- |
| 发送 / 成功 / 跳过 | 120 / 120 / 0 | 240 / 240 / 0 |
| 阶段末成功速率 | 3.82 次/秒 | 7.25 次/秒 |
| 在途请求峰值 | 1 | 1 |
| 平均处理耗时 | 0.1 秒 | 0.1 秒 |

把目标速率翻倍后，完成速率同步接近翻倍，而在途数量和平均耗时基本不变：处理本身只有
0.1 秒的延迟，`8 次/秒 × 0.1 秒` 的期望在途量不到 1，远低于 6 个并发上限，所以既没有跳过，
也没有排队等待。

## 图表结果

`screenshots/prometheus-targets.png` 是 Prometheus Targets 页面截图，`job="chat-app"`
的目标 `http://127.0.0.1:5001/metrics` 状态为 `UP`，说明采集成功。

`screenshots/grafana-dashboard.png` 是覆盖第一次完整模拟时间范围的仪表盘截图，可以看到：
成功速率在 burst 阶段升到约 4 次/秒后回落；平均耗时在 slow 阶段爬升到 3 秒并在其后的窗口里
逐渐回落；在途请求在 slow 阶段出现接近 6 的峰值，其余阶段基本贴着 0；失败速率只在 errors
阶段及之后的小段时间里出现。
