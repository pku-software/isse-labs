# Lab4：聊天应用指标监控

陈楷舜，2500018733。应用源自个人 Lab3 提交 `f69e8df3`，保留会话及消息的增删改查、原前端与聊天接口。

## Windows 本地启动

在个人 Fork 的 `isse-labs` 根目录使用 PowerShell：

```powershell
python -m venv lab4/2500018733-ChenKaishun/.venv
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe -m pip install -r lab4/2500018733-ChenKaishun/requirements.txt
& ./lab4/2500018733-ChenKaishun/start-app.ps1
```

使用 Python 3.13.5 验证；本次安装 Flask 3.1.3、requests 2.34.2、prometheus-client 0.26.0。
应用以单进程多线程运行，监听 `127.0.0.1:5001`。端口占用时为启动脚本传入 `-Port <可用端口>`，并同步修改 `prometheus.yml` 中的目标地址。

- 聊天页面：`http://127.0.0.1:5001/`
- 指标文本：`http://127.0.0.1:5001/metrics`
- 实验状态：`http://127.0.0.1:5001/api/lab/status`

应用数据写入个人目录的 `.runtime/app/conversations.json`，该目录和 `.venv/`、`.tools/` 均被忽略，不纳入提交。运行路径依据脚本位置确定，不受当前终端目录影响。

## mock 与 real 模式

默认 `CHAT_MODE=mock`：返回固定测试回复，不读取 `.env`，不调用外部模型。实验状态接口返回 `{"mode":"mock","external_model_calls":false}`。

原 `POST /api/messages` 和 `POST /api/conversations/<id>/messages` 接口支持以下 JSON：

```json
{"message":"非敏感测试消息","mock_delay_seconds":0.1,"mock_force_error":false}
```

延迟必须是 0～30 秒的有限数字，失败开关必须为布尔值。延迟在后端处理期间发生，强制失败返回 HTTP 503 和明确的错误 JSON。成功返回 HTTP 201，包含 `id`、`message`、`reply`。mock 仍执行原来的请求校验、会话查找与成功结果保存。

显式传入 `-Mode real` 才启用原 DeepSeek 调用，此时密钥仅从 `DEEPSEEK_API_KEY` 环境变量取得，实验状态接口返回 404，mock 参数不影响真实调用。监控实验使用 mock。

原存储锁及同一会话历史变化检查保留，多个会话可并发处理；同一会话同时修改历史可能返回 HTTP 409。

## 指标

| 指标 | 类型 | 记录范围 |
| --- | --- | --- |
| `chat_requests_total{outcome="success或error"}` | Counter | 聊天 POST 完成后的成功或失败次数；两种标签初始化为 0 |
| `chat_inprogress_requests` | Gauge | 当前尚未结束的聊天 POST 数量 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时，包含失败；单位秒 |

计数范围涵盖原聊天处理函数的校验、模型回复和保存。`finally` 负责记录耗时与结果，并减少在途数量，包含预期 HTTP 错误和未处理异常。耗时不含客户端网络传输。

Histogram 桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30、60 秒及正无穷。`_bucket` 记录不超过各边界的累计样本数，`_sum` 记录耗时总和，`_count` 记录样本总数。

页面、`/metrics`、状态接口及会话/消息的查询、修改、删除不计入聊天指标。标签不含消息内容、会话 ID 或用户身份。

## 应用验证

在仓库根目录运行：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe -m unittest discover -s lab4/2500018733-ChenKaishun -p test_app.py -v
```

测试使用独立临时聊天数据，覆盖成功与失败指标、异常收尾、输入校验、非聊天接口排除、原 CRUD、real/mock 路径区分，以及两个慢请求并发时的指标读取。测试禁止实际外部模型调用。

`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 是课程 `63c1038` 版本的个人副本。访问适配器中的三个函数用于核验 mock 状态、构造聊天请求和判断响应。

`project_adapter.py` 通过 `GET /api/lab/status` 严格核验 `mode=mock` 且 `external_model_calls=false`，禁止重定向和非本机目标。每个工作线程通过原会话创建接口建立独立会话，并在该线程内复用；聊天请求发送到 `POST /api/conversations/<id>/messages`，携带 `message`、`mock_delay_seconds` 和 `mock_force_error`。只有 HTTP 201 且返回有效 ID、消息字段及非空回复时判定成功。

课程调度器保持原样。创建会话发生在构造聊天请求时，不计入聊天业务指标，也不包含在调度器记录的单次聊天客户端耗时中，但会占用该工作线程的时间。调度器每个阶段建立自己的线程池。

适配器通过非 mock HTTP 服务拒绝测试、重定向拒绝测试、线程间会话隔离测试、响应判断测试，以及实际应用的一次成功和一次模拟失败请求验证后，设为 `ADAPTER_READY=True`。回归检查命令：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe -m unittest discover -s lab4/2500018733-ChenKaishun -p test_adapter.py -v
```

## Prometheus 与 Grafana

安装脚本固定使用 [Prometheus 3.15.0](https://github.com/prometheus/prometheus/releases/tag/v3.15.0) 和 [Grafana OSS 13.2.4](https://grafana.com/grafana/download/13.2.4?edition=oss&platform=windows) 的 Windows x64 官方包。安装时验证脚本中固定的 SHA-256，下载中断后可重复运行以复用完整分块。

在仓库根目录使用已创建的虚拟环境：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/install-monitoring.py
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/start-monitoring.py
```

启动脚本同时启动 mock 聊天应用、Prometheus 和 Grafana，启动前要求 5001、9090、3001 端口空闲。若之前在终端中运行了 `start-app.ps1`，先在该终端用 Ctrl+C 停止它，再启动整套服务。启动失败会停止本次脚本已启动的进程；成功后进程记录写入 `.runtime/processes.json`。

也可以添加 `--service app`、`--service prometheus` 或 `--service grafana` 分别启动某个尚未运行的服务；此时只检查该服务的端口。Windows 后台进程使用隐藏控制台，并将标准输出与错误写入对应的 `.runtime/<服务名>/`。

本机实验中 Grafana 后台运行曾出现无响应，因此建议分别启动应用和 Prometheus，并在独立 PowerShell 终端前台运行 Grafana，保持该终端开启：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/start-monitoring.py --service app
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/start-monitoring.py --service prometheus
& ./lab4/2500018733-ChenKaishun/start-grafana.ps1
```

已运行的服务不重复启动。`grafana.ini` 禁用了本实验不使用的数据源插件，保留 Prometheus 数据源；前台方式与后台方式使用同一份数据库和仪表盘配置。

| 服务 | 地址与配置 |
| --- | --- |
| 聊天应用 | `http://127.0.0.1:5001/`，单进程多线程 |
| Prometheus Targets | `http://127.0.0.1:9090/targets` |
| Grafana 仪表盘 | `http://127.0.0.1:3001/d/lab4-chat` |

3000 端口已有其他程序，因此 Grafana 使用 3001。三个服务均只绑定 `127.0.0.1`。Grafana 允许本机匿名只读查看，数据源与仪表盘由配置文件导入；管理账户的随机密码保存在被忽略的 `.runtime/grafana/admin-password.txt` 中。

相对于个人目录，下载包、分块及校验文件位于 `.tools/downloads/`，解压目录固定为 `.tools/prometheus/` 和 `.tools/grafana/`。Prometheus 时间序列存入 `.runtime/prometheus/`；Grafana 的数据库、日志、插件和仪表盘运行副本分别放在 `.runtime/grafana/data/`、`logs/`、`plugins/`、`dashboards/`。源码配置与可导入的 `grafana-dashboard.json` 保留在可提交目录。

Prometheus 的实际参数为：

```text
prometheus.exe --config.file=<个人目录>/prometheus.yml --storage.tsdb.path=<个人目录>/.runtime/prometheus --web.listen-address=127.0.0.1:9090 --storage.tsdb.retention.time=7d
```

Grafana 的实际参数为 `grafana.exe server --homepath <个人目录>/.tools/grafana --config <个人目录>/grafana.ini`；启动脚本通过 `GF_PATHS_DATA`、`GF_PATHS_LOGS`、`GF_PATHS_PLUGINS` 和 `GF_PATHS_PROVISIONING` 指定各路径。

`prometheus.yml` 每 2 秒采集一次 `127.0.0.1:5001/metrics`，超时 1 秒，job 为 `chat-app`。Grafana 数据源地址为 `http://127.0.0.1:9090`，UID 固定为 `lab4-prometheus`。启动脚本自动导入；若手工导入仪表盘，应先按 `grafana-provisioning/datasources/prometheus.yml` 建立同 UID 的数据源，或将 JSON 中的数据源 UID 换成目标实例的 UID。

仪表盘每 2 秒刷新，三个查询如下：

| 图表 | PromQL | 单位与意义 |
| --- | --- | --- |
| 成功 / 失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 请求/秒；最近 30 秒窗口内的平均完成速率 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 请求数；当前在途处理数量 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 秒；最近 30 秒窗口内的服务端平均耗时 |

平均耗时查询在没有新请求时可能得到无值，面板保留空缺。应用重启后内存指标重新累计，Prometheus 已采集的历史仍在其数据目录中。

2026-10-14 的本地连接核验中，`chat-app` 的采集地址为 `http://127.0.0.1:5001/metrics`，Target 为 `UP`；Grafana 数据源健康检查为 `OK`，三个面板查询均返回 HTTP 200。通过原聊天接口发送一条延迟 0.1 秒的 mock 请求后，平均耗时查询取得约 0.105 秒。此为连接核验，不是五阶段访问模拟结果。
## 访问模拟与实验结果

在仓库根目录、三个服务运行且应用处于 mock 模式时执行：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/simulate_traffic.py --base-url http://127.0.0.1:5001 --output lab4/2500018733-ChenKaishun/results/first-run.json
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --slow-delay 1 --phase-seconds 30 --slow-rate 2 --concurrency 6 --output lab4/2500018733-ChenKaishun/results/changed-run.json
```

以上为本次运行参数；再次复现时更换输出文件名，以保留本次结果。两次均使用并发上限 6。结果 JSON 时间为 UTC，下表为北京时间（UTC+8），日期均为 2026-10-14。每阶段计划发送 30 秒，结束时间包含等待在途请求完成的时间。

首次完整模拟结果见 [first-run.json](results/first-run.json)：

| 阶段 | 北京时间 | 目标频率（次/秒） | 模拟延迟（秒） | 计划 | 实发 | 成功 | 业务/HTTP 错误 | 跳过 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 20:13:40–20:14:10 | 1 | 0.1 | 30 | 30 | 30 | 0 | 0 |
| burst | 20:14:10–20:14:40 | 4 | 0.1 | 120 | 120 | 120 | 0 | 0 |
| slow | 20:14:40–20:15:12 | 2 | 3 | 60 | 52 | 52 | 0 | 8 |
| errors | 20:15:12–20:15:42 | 1 | 0.1 | 30 | 30 | 20 | 10 | 0 |
| recovery | 20:15:42–20:16:12 | 1 | 0.1 | 30 | 30 | 30 | 0 | 0 |

首次实际发送 262 次，其中成功 252 次、模拟失败 10 次。所有阶段的传输错误和非预期结果均为 0，运行未中断。burst 阶段成功完成速率升高，图中峰值约 3.96 次/秒；slow 阶段在途数量和平均耗时升高；errors 阶段出现失败速率；recovery 阶段恢复成功处理。模拟错误期间 Target 仍为 UP，因为指标采集能够正常完成。

第二次仅运行 slow 场景，时间为 20:29:29–20:30:00，结果见 [changed-run.json](results/changed-run.json)。固定目标频率每秒 2 次、并发上限 6，仅将模拟延迟从 3 秒降为 1 秒：

| 对比项 | 首次 slow | 第二次 slow |
| --- | --- | --- |
| 模拟延迟 | 3 秒 | 1 秒 |
| 平均耗时曲线峰值（30 秒窗口） | 3.012 秒 | 1.014 秒 |
| 采集到的在途数量峰值 | 6 | 2 |
| 计划发送数 | 60 | 60 |
| 实际发送数 / 成功数 | 52 / 52 | 60 / 60 |
| 跳过发送机会 | 8 | 0 |
| 脚本记录的客户端平均耗时 | 3.092 秒 | 1.078 秒 |

延迟缩短后，请求更快结束，在途数量减少，并发名额更快释放，脚本完成全部计划发送。跳过的 8 次是未发出请求的发送机会，不属于服务器失败请求。第二次无跳过表明本次负载下并发容量足够；提高频率后仍可能达到上限。

服务端平均耗时曲线与客户端平均耗时采用不同计量范围，表中的曲线峰值也不是整个阶段的平均值。耗时在请求结束时记录，查询又使用 30 秒窗口，因此曲线变化滞后于阶段切换。Prometheus 每 2 秒采集一次，短请求的在途峰值可能没有被采到。

### 原始截图与仪表盘

- [Prometheus Target UP 原图](screenshots/prometheus-targets.png)
- [完整五阶段 Grafana 原图](screenshots/grafana-dashboard.png)，时间范围为 20:13:30–20:16:32，包含三个面板与图例。
- [Grafana 仪表盘 JSON](grafana-dashboard.json)，从本次实际运行的仪表盘 API 导出，导入所需数据源 UID 为 `lab4-prometheus`。
