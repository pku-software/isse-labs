# 聊天应用本地监控

基于 Lab 3 `2400017727-JiangXuqi` 的 Flask 应用，保留聊天记录的创建、查看、修改和删除。

## 运行应用

在本目录创建 `.venv` 并安装 `requirements.txt`，然后执行：

```bash
MODEL_MODE=mock .venv/bin/python app.py
```

默认地址为 http://127.0.0.1:5001，可用 `PORT` 修改端口。单进程、线程并发运行，聊天记录仅存在内存中。

默认 `MODEL_MODE=mock`，不调用外部模型、不读取 `.env`。`MODEL_MODE=real` 保留原 DeepSeek 功能，凭据仅从进程环境 `DEEPSEEK_API_KEY` 获取；本实验使用 mock。

## 接口

- `POST /api/messages`：JSON `{"message":"测试消息"}`，成功返回 201 和 `id`、`message`、`reply`。
- mock 可追加 `"mock":{"delay_seconds":3,"force_error":false}`，延迟允许 0–10 秒；强制失败返回 503。
- `GET /api/messages`、`PATCH /api/messages/<id>`、`DELETE /api/messages/<id>`：聊天记录增删改查。
- `GET /api/lab-status`：返回实际运行模式与外部模型调用是否启用。
- `GET /metrics`：Prometheus 文本格式指标。

## 指标

仅 `POST /api/messages` 计入聊天业务指标，包括失败请求。消息正文与记录 ID 不作为标签。

| 指标 | 含义 |
| --- | --- |
| `chat_requests_total{outcome="success或error"}` | 已完成聊天请求累计次数 |
| `chat_inprogress_requests` | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | 服务端聊天耗时 Histogram，单位秒，包含失败请求 |

工具包位于 `.tools/`，运行数据位于 `.runtime/`，虚拟环境位于 `.venv/`，均由个人忽略规则排除。

## 本地 Prometheus 与 Grafana（Linux x86_64）

官方稳定版本：Prometheus 3.15.0、Grafana OSS 13.2.4。下载来源及 SHA256 固定在 `install_tools.py`，解压前验证摘要。首次安装：

```bash
python3 install_tools.py
python3 start_services.py
```

启动脚本可重复运行，按个人 PID 文件识别已经启动的服务；端口被其他程序占用时会报错，不会关闭其他服务。也可用 `--service app`、`--service prometheus`、`--service grafana` 分别启动。

| 服务 | 本地地址 | 数据与日志 |
| --- | --- | --- |
| 应用 | http://127.0.0.1:5001 | `.runtime/app/` |
| Prometheus | http://127.0.0.1:9090 | `.runtime/prometheus/` |
| Grafana | http://127.0.0.1:3000 | `.runtime/grafana/data/`、`log/`、`plugins/` |

工具解压到 `.tools/prometheus/` 和 `.tools/grafana/`，下载包及校验文件在 `.tools/downloads/`。全部运行路径由 `start_services.py` 显式设置，监听地址均为 `127.0.0.1`。

Prometheus 的实际命令（在个人目录中执行）：

```bash
.tools/prometheus/prometheus --config.file="$PWD/prometheus.yml" --storage.tsdb.path="$PWD/.runtime/prometheus" --web.listen-address=127.0.0.1:9090
```

Grafana 的实际命令：

```bash
LAB4_ROOT="$PWD" \
GF_PATHS_DATA="$PWD/.runtime/grafana/data" \
GF_PATHS_LOGS="$PWD/.runtime/grafana/log" \
GF_PATHS_PLUGINS="$PWD/.runtime/grafana/plugins" \
GF_PATHS_PROVISIONING="$PWD/config/grafana/provisioning" \
GF_DASHBOARDS_MIN_REFRESH_INTERVAL=2s \
.tools/grafana/bin/grafana server --homepath="$PWD/.tools/grafana" --config="$PWD/grafana.ini"
```

推荐用启动脚本，它还会创建所需目录并将可导入的仪表盘复制到 `.runtime/grafana/dashboards/`，供文件配置加载。

`prometheus.yml` 每 2 秒采集 `127.0.0.1:5001/metrics`，超时 1 秒，job 为 `chat-app`。Targets 页面为 http://127.0.0.1:9090/targets 。

Grafana 自动配置数据源 `Lab4 Prometheus`（UID `lab4-prometheus`），地址 `http://127.0.0.1:9090`。本地启用匿名只读查看，仪表盘地址为 http://127.0.0.1:3000/d/lab4-chat-monitoring ，每 5 秒刷新。

### 三个 Panel

1. 成功/失败请求速率：`sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`，表示最近 30 秒平均每秒完成请求数。
2. 正在处理的请求：`sum(chat_inprogress_requests{job="chat-app"})`，表示采集时刻在途聊天处理数。
3. 平均处理耗时：`sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`，表示最近 30 秒服务端平均耗时，单位秒，包含失败；无请求时允许无值。

Histogram 的 `_bucket{le="上界"}` 是耗时不超过该上界的累计样本数，`_sum` 是耗时总和，`_count` 是样本数。平均耗时使用总和与次数的增长率计算。

`grafana-dashboard.json` 可在 Grafana 导入。导入到其他环境时，先添加 Prometheus 数据源，再在仪表盘顶部的“Prometheus 数据源”下拉框选择它。文件配置位于 `config/grafana/provisioning/`。

官方来源：[Prometheus 下载](https://prometheus.io/download/)、[Grafana OSS 下载](https://grafana.com/grafana/download/13.2.4?edition=oss&platform=linux)。

## 访问模拟与实际结果

`simulate_traffic.py` 直接复制课程调度器并保持原样。`project_adapter.py` 实现三个项目适配点：通过 `GET /api/lab-status` 读取并核验 mock 且外部模型调用关闭；构造原 `POST /api/messages` 请求；结合 HTTP 201 和有效聊天记录判断成功。模拟错误 HTTP 503 被识别为失败。本地地址限制和禁止重定向的检查保留。

首次完整模拟命令（在个人目录执行）：

```bash
.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
```

第二次仅将 slow 后端延迟从 3 秒改为 5 秒，其他设置保持默认（目标每秒 2 次、并发上限 6）：

```bash
.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --slow-delay 5 --phase-seconds 30 --output results/changed-run.json
```

两份 JSON 是真实运行结果。以下时间均为 Asia/Singapore（UTC+8）；JSON 内使用 UTC。默认各阶段发送持续 30 秒，阶段结束还会等待在途请求完成，故阶段实际结束时间可能超过 30 秒。脚本最终额外等待 10 秒供采集器记录。

### 首次完整模拟

| 阶段 | 开始时间 | 结束时间 | 成功 | 业务/HTTP错误 | 跳过 |
| --- | --- | --- | ---: | ---: | ---: |
| baseline | 2026-10-15 19:30:57 | 2026-10-15 19:31:27 | 30 | 0 | 0 |
| burst | 2026-10-15 19:31:27 | 2026-10-15 19:31:57 | 120 | 0 | 0 |
| slow | 2026-10-15 19:31:57 | 2026-10-15 19:32:29 | 52 | 0 | 8 |
| errors | 2026-10-15 19:32:29 | 2026-10-15 19:32:59 | 20 | 10 | 0 |
| recovery | 2026-10-15 19:32:59 | 2026-10-15 19:33:29 | 30 | 0 | 0 |

首次累计发送 262 次，成功 252 次，预设失败 10 次，网络错误及非预期结果均为 0。正常低频阶段约每秒 1 次，burst 提高到每秒 4 次，slow 使用 3 秒后端延迟，errors 每第 3 次请求模拟失败，recovery 恢复低频和 0.1 秒延迟。

Prometheus 历史查询显示：成功请求速率峰值约 3.96 次/秒，失败请求速率峰值约 0.32 次/秒，在途请求峰值为 6，服务端平均耗时峰值约 3.001 秒。恢复后在途数回落，耗时与错误速率受 30 秒窗口影响逐渐回落。

`screenshots/grafana-dashboard.png` 为首次完整模拟的浏览器原始截图；`screenshots/prometheus-targets.png` 显示应用 `chat-app` 的 `127.0.0.1:5001/metrics` 为 UP。

### 第二次参数变化

第二次 slow 从 2026-10-15 20:00:36 运行到 2026-10-15 20:01:10。

| 比较项 | 首次 slow，延迟 3 秒 | 第二次 slow，延迟 5 秒 |
| --- | ---: | ---: |
| 发送机会 | 60 | 60 |
| 实际发送且成功 | 52 | 35 |
| 跳过发送 | 8 | 25 |
| 网络错误 / 非预期结果 | 0 / 0 | 0 / 0 |
| 客户端平均耗时 | 约 3.027 秒 | 约 5.025 秒 |
| 服务端平均耗时曲线峰值 | 约 3.001 秒 | 约 5.001 秒 |
| 在途请求曲线峰值 | 6 | 6 |

后端延迟增加后，每个请求占用并发名额更久，在途数量仍受并发上限 6 约束，因此完成数量减少、跳过发送机会增多。客户端平均耗时包含网络开销，不等同于服务端 Histogram；上表分别列出这两类真实观测。

### 读图与复现

`rate(...[30s])` 使用最近 30 秒窗口，所以阶段切换不会表现为瞬间跳变，恢复也有延迟。2 秒一次的采集可能错过 0.1 秒请求的短暂在途峰值。调度器达到并发上限时跳过发送机会，不无限排队，因此目标发送速率与实际发送、完成速率可能不同。

复现时先建立个人虚拟环境并安装依赖，再安装工具并启动服务：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
python3 install_tools.py
python3 start_services.py
```

若当前 Linux Python 缺少 ensurepip，本次实际使用官方引导脚本补齐个人虚拟环境内的 pip：

```bash
mkdir -p .tools/downloads
python3 -m venv --without-pip .venv
curl --fail --location https://bootstrap.pypa.io/get-pip.py --output .tools/downloads/get-pip.py
.venv/bin/python .tools/downloads/get-pip.py
.venv/bin/python -m pip install -r requirements.txt
```

创建虚拟环境、下载和运行工具前，应先确认个人忽略规则实际生效且运行目录没有被跟踪；`install_tools.py` 与 `start_services.py` 会检查工具和运行目录的规则。复现时使用新的结果文件名可保留已有两次结果。采集数据是本地运行数据，重新安装后需重新运行脚本才能产生新的历史曲线。
