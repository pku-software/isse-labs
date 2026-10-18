# Lab 4：陈川泽 2300017804

基于本人 Lab 3 的 Flask 聊天应用，保留原 HTML/CSS/JavaScript 页面、多轮会话和消息增删改查。Lab 4 在本地使用 mock 回复，通过真实 HTTP 请求记录聊天指标。

## 应用运行

环境为 macOS / Apple Silicon，终端为 zsh。以下命令在本个人目录执行：

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
CHAT_MODE=mock .venv/bin/python -B app.py
```

应用以单进程、多线程方式监听 `127.0.0.1:5001`，关闭 debug 和自动重载。需要更换端口时可设置 `PORT`，并同步修改个人 `prometheus.yml` 的 target。前台运行时按 Ctrl+C 停止。

- 页面：`http://127.0.0.1:5001/`
- 模拟状态：`http://127.0.0.1:5001/api/status`
- 指标：`http://127.0.0.1:5001/metrics`

默认 `CHAT_MODE=mock`，无需 Key，不导入或创建真实模型客户端，也不读取 `.env`。`/api/status` 根据启动配置返回 `{"mode":"mock","external_model_calls":false}`。原真实模型调用保留在 `real` 分支，只从运行环境读取 `DEEPSEEK_API_KEY`；本实验不启用该分支。real 模式的实验状态接口返回 404，模拟参数不会改变真实调用行为。

本次聊天数据保存在 `.runtime/app/mock-conversations.json`，与原 Lab 2/3 数据隔离；real 模式使用独立文件。存储使用锁保护 ID 分配、读写和 JSON 序列化，文件先写临时文件再替换。生成回复期间不持有全局存储锁；同一会话的并发请求各自使用开始时的历史快照，按完成顺序追加完整问答。回复期间会话被删除时返回 409。

## 聊天请求与模拟参数

原有两个聊天入口均保留：

- `POST /api/messages`：单消息聊天。
- `POST /api/conversations/<id>/messages`：页面使用的多轮会话聊天。

请求正文中的 `message` 是非空字符串。mock 模式还接受：

| 字段 | 默认 | 含义 |
| --- | --- | --- |
| `mock_delay` | `0.1` | 服务端处理期间等待的秒数，接受 0～10 的有限数字。 |
| `mock_error` | `false` | 为 `true` 时，在等待后返回 HTTP 503 和 `code: mock_error`。 |

成功响应为 HTTP 201，包含 `id`、`message`、`reply`；固定回复说明当前是本地 mock。参数无效返回 400。模拟失败不写入聊天记录。

## 指标

指标定义位于 `metrics.py`，`/metrics` 使用 `prometheus_client` 的标准文本输出及内容类型。

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 聊天处理结束后的累计次数，按最终结果区分。 |
| `chat_inprogress_requests` | Gauge | 正在处理的聊天请求数量。 |
| `chat_request_duration_seconds` | Histogram | 从进入聊天处理到形成响应的服务端耗时，单位秒。 |

两个聊天 POST 入口统计正常回复、模拟失败、参数错误和意外异常；请求结束时完成指标收尾。会话管理、消息编辑/删除、静态资源、状态检查及指标采集本身不计入聊天指标。标签仅包含固定结果值，不包含消息内容或用户标识。

耗时桶上界为 `0.05、0.1、0.25、0.5、1、2、3、5、10、30、60、+Inf` 秒，同时输出耗时总和 `_sum` 和观测次数 `_count`。进程重启后内存指标重新开始累计。页面发出的聊天请求、Agent 的聊天接口验证都会产生真实计数。

## 本地验证

```sh
.venv/bin/python -B -m unittest -v test_app
```

测试使用 `.runtime/app/` 下自动清理的独立临时存储，不读取 `.env`、不调用外部模型。覆盖原会话/消息 CRUD、多轮历史、成功与模拟错误计数、非聊天请求排除、无效模拟参数、异常收尾、模式报告，以及六个并发慢请求期间的实际 HTTP 指标采集和存储完整性。

2026-10-18 在 Python 3.13.13、Flask 3.1.3、prometheus-client 0.26.0 下，7 项测试通过。实际本地 HTTP 验证中，页面、静态资源和 mock 状态接口均返回 200；正常聊天返回 201，模拟失败返回 503。六个并发慢请求期间，指标接口在 0.5 秒超时限制内成功返回并显示 6 个在途请求，全部完成后回到 0，存储中的消息 ID 与会话轮次完整且无重复。真实模型依赖保留为 openai 2.54.0，验证没有调用真实模型。

本地演示服务另外接受了一次成功和一次模拟失败的接口检查，所以学生开始浏览前成功、错误累计值分别为 1、1，耗时观测次数为 2；临时测试消息已删除，指标仍保留本进程的累计值。测试进程和演示服务的指标彼此独立。

## 文件与运行目录

`simulate_traffic.py` 是课程访问调度器的个人副本，只发送 HTTP 请求；项目接口适配集中在 `project_adapter.py`，采集配置为 `prometheus.yml`。

工具下载包放在 `.tools/downloads/`，Prometheus 和 Grafana 分别解压到 `.tools/prometheus/`、`.tools/grafana/`。对应运行数据放在 `.runtime/prometheus/` 和 `.runtime/grafana/`，应用运行数据及日志放在 `.runtime/app/`，Python 环境放在 `.venv/`。这些目录及 `.env` 已被个人 `.gitignore` 排除；配置、仪表盘、`results/*.json` 和截图可正常提交。

参考：[Prometheus Python 指标类型](https://prometheus.github.io/client_python/instrumenting/)、[Histogram](https://prometheus.github.io/client_python/instrumenting/histogram/)。

## Prometheus 与 Grafana

本项目选择 Prometheus **3.15.0** 和 Grafana OSS **13.2.4** 的 macOS ARM64 稳定发行包。下载地址来自 [Prometheus 官方发行页](https://github.com/prometheus/prometheus/releases/tag/v3.15.0) 与 [Grafana 官方下载页](https://grafana.com/grafana/download/13.2.4?edition=oss&platform=mac)，安装前核对 SHA256。

在个人目录运行：

```sh
bash install-monitoring.sh
```

安装脚本先核验 Git 忽略规则和未跟踪状态，下载并校验发行包，再解压到固定 `.tools/` 子目录。已有正确校验值的包会复用。两个 SHA256 为：

```text
920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260  prometheus-3.15.0.darwin-arm64.tar.gz
a910966466359212f1d875748a72a4638c7d3724448d0c369210b31d763b165d  grafana_13.2.4_38252365904_darwin_arm64.tar.gz
```

启动时分别在三个终端中执行以下命令，保持它们运行；已启动的服务无需重复启动：

```sh
bash monitoring.sh app
bash monitoring.sh prometheus
bash monitoring.sh grafana
```

`monitoring.sh` 根据自身位置设置 `LAB4_ROOT`，显式指定工具、配置、数据库、日志及插件路径。Grafana 启动时把仪表盘副本复制到 `.runtime/grafana/dashboards/`，由 `grafana/provisioning/` 中的配置自动加载数据源和仪表盘。停止时在各自终端按 Ctrl+C，仅停止本项目进程。

| 程序 | 本地地址 | 数据位置 |
| --- | --- | --- |
| 聊天应用 | `http://127.0.0.1:5001/` | `.runtime/app/` |
| Prometheus | `http://127.0.0.1:9090/` | `.runtime/prometheus/`，保留 7 天 |
| Grafana | `http://127.0.0.1:3000/` | `.runtime/grafana/data/`、`logs/`、`plugins/` |

三个服务均只监听 `127.0.0.1`。本项目专用 Grafana 允许本机匿名只读查看，配置通过文件加载，无需输入账号密码。它使用 UID 为 `lab4-prometheus` 的数据源，地址为 `http://127.0.0.1:9090`。导入仪表盘到其他实例时，先使用本项目数据源配置，或把三个 Panel 的数据源改为该实例中的 Prometheus 数据源。

Prometheus 的 `chat-app` job 每 2 秒采集 `127.0.0.1:5001/metrics`，采集超时为 1 秒。Target 页面为 `http://127.0.0.1:9090/targets`。应用端口变化时修改 `prometheus.yml`；Prometheus 端口变化时同步修改启动脚本和 Grafana 数据源配置；Grafana 端口变化时同步修改 `grafana.ini` 的 `http_port` 和 `root_url`。

仪表盘 UID 为 `lab4-chat-2300017804`，每 2 秒刷新，默认显示最近 15 分钟。三个 Panel 使用：

**成功 / 失败请求速率**

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
```

按 outcome 分组，显示最近 30 秒内平均每秒完成的请求数，单位为次/秒。

**正在处理的请求**

```promql
sum(chat_inprogress_requests{job="chat-app"})
```

显示采集时刻正在执行的聊天请求数量。

**平均处理耗时**

```promql
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
/
sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

用窗口内耗时总和的增长率除以次数增长率，得到平均服务端耗时，单位秒。Histogram 的 `_bucket{le="3.0"}` 表示耗时不超过 3 秒的累计观测次数；各桶为累积桶，同一次观测可能计入多个上界。没有新请求或采集样本不足时，耗时图可能无值，配置不补零、不制造样本。

2026-10-19 本地安装验证：两个发行包均通过上述 SHA256 校验，程序报告 `darwin/arm64`、Prometheus 3.15.0 与 Grafana 13.2.4；`promtool check config prometheus.yml` 通过。Prometheus 实际 Target 的 job 为 `chat-app`、地址为 `http://127.0.0.1:5001/metrics`，状态为 `UP`，采集错误为空。查询成功、错误累计值分别为 2、1。Grafana 健康接口报告数据库正常，数据源健康检查成功查询 Prometheus API，浏览器实际显示三个 Panel，刷新间隔为 2 秒。

采集开始时此前的聊天已经完成，窗口内没有新增请求，因此成功/失败速率与在途数量为 0，平均耗时无有效数值。Grafana 的 macOS 启动日志包含读取 Linux `/proc` 进程启动时间失败的信息；上述健康、数据源、仪表盘实际验证通过。

Prometheus Target 原始截图：[chat-app 采集状态 UP](screenshots/prometheus-targets.png)。

## 访问模拟脚本

`simulate_traffic.py` 保持课程原版，负责发送节奏、有限并发和结果统计。`project_adapter.py` 负责本项目接口：

- `confirm_mock_mode()` 实际 GET `/api/status`，仅接受 `mode` 为 `mock` 且 `external_model_calls` 严格为布尔值 `false` 的响应；关闭系统代理并禁止重定向。
- `build_chat_request()` 构造 `POST /api/messages`，使用 `message`、`mock_delay` 和 `mock_error` 字段，延迟与失败由后端处理。
- `response_is_success()` 检查 HTTP 201 和完整的聊天记录 JSON；空回复、错误字段、无效 JSON 或其他状态均判为失败。

调度器保留本机地址限制和同源检查。正常执行先核验 mock 状态，核验失败就停止，不发送聊天请求。2026-10-19 单请求验证中，成功请求返回 201，强制失败返回 503；成功、失败 Counter 各增长 1，耗时观测次数增长 2，结束后在途数量为 0。适配器还拒绝非 mock 状态、外部调用开启或未明确关闭的状态，以及重定向响应。

三个本地服务启动后，在个人目录运行完整模拟：

```sh
.venv/bin/python -B simulate_traffic.py \
  --base-url http://127.0.0.1:5001 \
  --output results/first-run.json
```

默认依次运行 `baseline`、`burst`、`slow`、`errors`、`recovery` 五个阶段，每阶段 30 秒，并等待在途请求完成，最后再等 10 秒采集恢复状态。输出记录各阶段的实际时间、参数、发送/跳过数量及成功/错误计数；客户端耗时包含网络开销，与服务端 Histogram 的统计范围不同。

首次完整模拟的仪表盘原始截图：[三个 Panel 与完整时间范围](screenshots/grafana-dashboard.png)，时间范围为北京时间 2026-10-19 00:32:36～00:36:19。

## 两次实际运行结果

以下时间均为北京时间 2026-10-19；结果 JSON 中的时间使用 UTC，比北京时间早 8 小时。两份 JSON 均由上述原版调度器实际执行生成。

### 首次完整模拟

原始结果：[results/first-run.json](results/first-run.json)。每个阶段的发送时段为 30 秒，并发上限为 6，请求超时为 10 秒，所有阶段结束后等待 10 秒。正常、错误、恢复阶段的目标频率为每秒 1 次，延迟 0.1 秒；增加访问阶段为每秒 4 次，延迟 0.1 秒；慢回复阶段为每秒 2 次，延迟 3 秒。错误阶段每第 3 次请求强制失败。

| 阶段 | 实际起止时间（含在途收尾） | 发送 | 成功 | HTTP/业务错误 | 跳过 | 客户端平均耗时 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 00:32:56～00:33:26 | 30 | 30 | 0 | 0 | 0.120 秒 |
| burst | 00:33:26～00:33:56 | 120 | 120 | 0 | 0 | 0.120 秒 |
| slow | 00:33:56～00:34:28 | 52 | 52 | 0 | 8 | 3.017 秒 |
| errors | 00:34:28～00:34:58 | 30 | 20 | 10 | 0 | 0.118 秒 |
| recovery | 00:34:58～00:35:28 | 30 | 30 | 0 | 0 | 0.121 秒 |

共发送 262 次，成功 252 次，10 次失败均为预设的模拟错误；所有阶段的网络错误和非预期结果均为 0。

实际 Prometheus 查询和截图显示，成功请求速率峰值约为 4.00 次/秒，失败速率峰值约为 0.36 次/秒。在途请求峰值为 6，平均服务端耗时图的峰值约为 3.005 秒。正常阶段的 Gauge 采样均为 0，增加访问阶段采到了 0 和 1；0.1 秒的短请求可能完全落在两次间隔 2 秒的采集之间，所以 Gauge 的采样值不能代表该区间处理过的所有请求。慢回复持续更久，采集器能够看到多个请求同时在处理。

请求速率和平均耗时使用 30 秒窗口，因此阶段交界处表现为逐渐变化，而不是立即跳到新值。错误阶段结束后，窗口内仍包含先前的失败，错误速率随后才回落到 0。慢回复阶段虽计划每秒 2 次，但达到并发上限时跳过了 8 次发送机会；目标发送频率与实际发送、完成频率并不相同。

### 延迟改为 5 秒

第二次只运行慢回复场景，保持每秒 2 次、并发上限 6 和 30 秒发送时段，仅把后端延迟从 3 秒改为 5 秒：

```sh
.venv/bin/python -B simulate_traffic.py \
  --base-url http://127.0.0.1:5001 \
  --scenario slow --phase-seconds 30 --slow-delay 5 \
  --output results/changed-run.json
```

原始结果：[results/changed-run.json](results/changed-run.json)。实际阶段时间为 01:05:31～01:06:05，包含最后一批在途请求的收尾，之后再等待 10 秒。

| 比较项 | 首次 slow | 第二次 slow |
| --- | ---: | ---: |
| 后端设置延迟 | 3 秒 | 5 秒 |
| 计划发送机会 | 60 | 60 |
| 实际发送并成功完成 | 52 | 35 |
| 并发已满时跳过 | 8 | 25 |
| HTTP/业务错误、网络错误、非预期结果 | 均为 0 | 均为 0 |
| 客户端平均耗时 | 3.017 秒 | 5.018 秒 |
| 平均服务端耗时图峰值 | 约 3.005 秒 | 约 5.008 秒 |
| 采集到的在途请求峰值 | 6 | 6 |

第二次在途峰值仍为 6，因为两次均达到脚本的并发上限；延迟变长后，每个请求占用并发名额更久，跳过的发送机会从 8 增至 25，实际发送量减少。第二次成功请求速率图的峰值约为 1.11 次/秒。停止请求后在途数量回到 0，窗口中的完成速率也逐渐回到 0。窗口没有新请求时，平均耗时没有有效值；图例的 `Last *` 会保留最近一个有效值，不表示此时仍有请求正在处理。

两次模拟完成后，从实际运行的 Grafana 导出 [grafana-dashboard.json](grafana-dashboard.json)，保留三个查询和 `lab4-prometheus` 数据源引用，将实例专用的数值 `id` 清空以便导入。仪表盘默认仍显示最近 15 分钟；查看本次历史结果时选择上述绝对时间范围。运行数据库不纳入提交，从干净环境复现时，按前文启动三个服务并重新执行两次命令即可生成新的时间序列；使用新的 `--output` 文件名可保留本次结果。
