# Lab 4：聊天应用本地监控

本项目来自 `lab3/2500013175-wangxiaoyu` 的 Flask 聊天应用，保留 HTML/CSS/JavaScript 前端、会话与消息增删改查、原聊天接口。未迁移原聊天数据。

## 本地运行

当前环境为 macOS、Apple Silicon（arm64）、zsh、Python 3.14.8。从本个人目录运行：

```sh
python3 -m venv .venv
env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy \
  -u HTTPS_PROXY -u https_proxy .venv/bin/python -m pip --isolated install \
  --proxy '' --index-url https://pypi.org/simple -r requirements.txt
zsh run_app.sh
```

应用地址为 `http://127.0.0.1:5001/`，单进程、线程并发、不启用调试重载。可通过 `APP_PORT` 修改端口。聊天数据保存在 `.runtime/app/conversations.json`，工具、运行数据和虚拟环境分别放在 `.tools/`、`.runtime/`、`.venv/`，均不提交。

本机安装依赖时，已有 SOCKS 代理设置使新虚拟环境的 pip 安装失败；以上命令仅对安装进程移除代理变量并使用官方 PyPI，不修改系统代理配置。`requirements.txt` 固定本次实际验证的直接依赖版本：Flask 3.1.3、prometheus-client 0.26.0、OpenAI 3.29.0、httpx 0.28.1 和 socksio 1.0.0。

`MODEL_MODE` 默认为 `mock`，返回固定测试回复，不导入或创建模型客户端、不读取 `.env`，不需要 Key。`GET /api/lab/status` 反映 mock 模式与外部调用关闭状态；real 模式下该接口返回 404。保留 `MODEL_MODE=real` 的 DeepSeek 功能，只读取进程环境中的 `DEEPSEEK_API_KEY`；本实验使用 mock 模式。

前端聊天请求为 `POST /api/conversations/<id>/messages`，JSON 字段为 `message`；先通过 `POST /api/conversations` 创建会话。响应状态 201，包含 `user_message` 和 `assistant_message`。原 `POST /api/messages` 接口也保留。mock 模式可额外传入：

```json
{"message":"监控测试","mock":{"delay_seconds":0.1,"force_error":false}}
```

后端延迟限定为 0～30 秒。强制失败返回 503 和 `code: mock_failure`；mock 选项在 real 模式中不改变模型调用。共享存储通过锁保护，模型等待期间释放锁，避免阻塞指标采集。

## 指标

`GET /metrics` 返回 prometheus-client 的标准文本格式与内容类型。仅统计两个 POST 聊天接口的处理，不统计 CRUD、静态资源、状态接口与指标采集。

| 指标 | 含义 |
| --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | 完成的成功或失败聊天处理累计次数，包含聊天接口校验失败 |
| `chat_inprogress_requests` | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | 服务端处理耗时 Histogram，失败路径也记录 |

Histogram 的有限桶上界为 0.05、0.1、0.25、0.5、1、2、3、5、10、30 秒，另有标准 `+Inf` 桶；同时输出耗时总和 `_sum` 和观测次数 `_count`。指标标签不包含聊天内容或请求 ID。无论正常返回还是异常，都会记录结果与耗时并减少在途数量。

HTTP 核验中，正常请求返回 201、模拟失败返回 503；两条 1 秒慢请求同时处理时，在途数量为 2，指标接口响应约 0.016 秒，处理结束后回到 0。会话与消息 CRUD 通过，非聊天访问未改变指标。随后通过前端发送 3 条测试消息，累计成功 5、失败 2，耗时观测次数为 7；这些为启动后的验证计数，服务重启后累计值重新开始。

## 课程访问脚本

`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 来自课程 `lab4/starter/`。采集配置为 2 秒间隔、1 秒超时，应用目标地址为 `127.0.0.1:5001`。调度脚本通过 HTTP 访问应用，适配器负责对应项目接口。

调度器保持与课程原件完全一致，负责发送节奏、并发上限、阶段切换和真实结果统计。个人 `project_adapter.py` 的三个适配函数为：

- `confirm_mock_mode()`：在本机根地址 GET `/api/lab/status`，验证 `mode="mock"` 且 `external_model_calls=false`；成功后 POST `/api/conversations` 创建本次测试会话。禁用 HTTP 重定向和系统代理，不访问其他主机。
- `build_chat_request()`：向 `/api/conversations/<本次会话ID>/messages` 发送 POST JSON，字段为 `message` 和 `mock` 下的 `delay_seconds`、`force_error`。
- `response_is_success()`：要求 HTTP 201，且响应中用户与助手消息的角色、ID 和非空内容有效；503 模拟错误或无效 JSON 均判为失败，不打印消息正文。

适配器单请求核验中，正常请求返回 201、强制错误返回 503，结果判断正确；非本机地址被拒绝。`ADAPTER_READY=True` 仅在单请求核验通过后启用。

对临时 real 模式服务的 HTTP 核验中，适配器返回 False，课程脚本退出码为 2，聊天指标仍为零，未发出真实聊天请求；该临时服务已停止。

## Prometheus 与 Grafana

官方稳定版：Prometheus 3.15.0、Grafana OSS 13.2.3，均为 macOS arm64。安装程序从官方 GitHub Releases 和 `dl.grafana.com` 下载并验证官方 SHA256；下载包与校验文件放在 `.tools/downloads/`，解压位置分别为 `.tools/prometheus/`、`.tools/grafana/`。安装前自动核验忽略规则和未跟踪状态。

在本个人目录运行；应用保持启动，两个监控程序分别使用一个终端：

```sh
.venv/bin/python install_tools.py
zsh run_prometheus.sh
zsh run_grafana.sh
```

Prometheus 监听 `127.0.0.1:9090`，读取本目录的 `prometheus.yml`，时间序列保存到 `.runtime/prometheus/`。Targets 页面为 `http://127.0.0.1:9090/targets`。`UP` 表示指标采集成功。

Grafana 监听 `127.0.0.1:3000`，数据、日志、插件、运行中的仪表盘副本分别放到 `.runtime/grafana/data/`、`log/`、`plugins/`、`dashboards/`。启动脚本复制根目录的仪表盘 JSON，并从 `grafana/provisioning/` 自动配置数据源和仪表盘。启用本机匿名 Viewer，浏览仪表盘无需登录。

数据源 `Lab4 Prometheus`（UID `lab4-prometheus`）指向 `http://127.0.0.1:9090`。仪表盘地址为 `http://127.0.0.1:3000/d/lab4-chat`，使用浏览器时区、默认显示最近 15 分钟、每 2 秒刷新。三个时间序列 Panel 的查询为：

| Panel | PromQL 与含义 |
| --- | --- |
| 成功 / 失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`：最近 30 秒内平均每秒完成的请求数，按结果分两条线，非累计次数 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})`：采集时正在处理的聊天数量，非在线用户数 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`：窗口内耗时总和增速除以观测次数增速，单位秒，包含失败请求 |

Histogram 的 `_bucket{le="0.25"}` 表示耗时不超过 0.25 秒的累计观测数；各桶为累积桶，`+Inf` 包含所有观测。本仪表盘使用 `_sum` 与 `_count` 计算平均值。没有请求的窗口可能无值，不补造零值。

可在另一 Grafana 实例导入 `grafana-dashboard.json`：先创建指向本机 Prometheus 的数据源，导入后在仪表盘顶部“Prometheus 数据源”下拉框选择它。JSON 中的三个 Panel 引用该数据源变量，不依赖原实例的数据库。

已核验 Prometheus Target `chat-app` 的实际地址为 `http://127.0.0.1:5001/metrics`、健康状态 `up`、采集错误为空；Grafana 数据源健康检查返回 `OK`，三个查询均可执行。原始截图 `screenshots/prometheus-targets.png` 显示应用 Target 为 `UP`，补充图 `screenshots/prometheus-query.png` 显示成功 5、失败 2 的累计次数。

## 首次完整模拟

应用、Prometheus 和 Grafana 保持启动，在本个人目录执行：

```sh
.venv/bin/python -u simulate_traffic.py \
  --base-url http://127.0.0.1:5001 --output results/first-run.json
```

使用默认参数：五阶段各 30 秒，正常/错误/恢复阶段目标频率 1 次/秒，burst 4 次/秒，slow 2 次/秒，正常延迟 0.1 秒、slow 延迟 3 秒，并发上限 6，错误阶段每第 3 次失败，单请求超时 10 秒，末尾等待采集 10 秒。

运行日期为 2026-10-12；下表显示北京时间，结果 JSON 的实际起止时间为 UTC。慢阶段结束后等待在途请求完成，因此实际结束晚于 30 秒的调度窗口。

| 阶段 | 实际时间 | 发送 | 成功 | 业务/HTTP 错误 | 跳过 |
| --- | --- | --- | --- | --- | --- |
| baseline | 20:21:44–20:22:14 | 30 | 30 | 0 | 0 |
| burst | 20:22:14–20:22:44 | 120 | 120 | 0 | 0 |
| slow | 20:22:44–20:23:17 | 52 | 52 | 0 | 8 |
| errors | 20:23:17–20:23:47 | 30 | 20 | 10 | 0 |
| recovery | 20:23:47–20:24:17 | 30 | 30 | 0 | 0 |

合计发送 262、成功 252、预设失败 10；各阶段网络错误与非预期结果均为 0，脚本退出码为 0。JSON 中的 `client_mean_seconds` 包含 HTTP 开销，不是服务端 Histogram。

Prometheus 在首次运行范围的真实查询结果中，成功速率最大为 4 次/秒，error 速率最大约 0.321 次/秒，在途数量最大为 6，服务端窗口平均耗时最大约 3.007 秒。慢阶段的并发名额满时跳过 8 次发送机会，目标频率与实际完成速率不同；burst→slow 也同时改变了目标频率。正常请求只持续约 0.1 秒，2 秒采集可能漏掉在途短峰值。速率和平均耗时使用 30 秒窗口，阶段边界被平滑，恢复有滞后。

学生原始整体截图为 `screenshots/grafana-dashboard.png`，覆盖北京时间 20:21:34–20:24:57，包含完整模拟与收尾状态。三幅补充细节图为 `grafana-request-rate.png`、`grafana-inprogress.png`、`grafana-duration.png`，均位于 `screenshots/`。

## 调整延迟后的模拟

仅将 slow 后端延迟从 3 秒改为 8 秒；目标频率保持 2 次/秒、并发上限保持 6，单跑 slow 场景，调度窗口仍为 30 秒，末尾等待 10 秒。使用命令：

```sh
.venv/bin/python -u simulate_traffic.py \
  --base-url http://127.0.0.1:5001 --scenario slow \
  --phase-seconds 30 --slow-delay 8 --output results/changed-run.json
```

真实结果写入 `results/changed-run.json`，未覆盖首次结果。实际运行时间为 2026-10-12 北京时间 21:46:58–21:47:34，等待在途请求收尾使实际时长超过 30 秒。发送 24 次、成功 24 次、跳过 36 次发送机会，业务/HTTP 错误、网络错误、非预期结果均为 0，脚本退出码为 0。客户端平均耗时约 8.021 秒。

| 实际结果 | 首次 slow（3 秒） | 第二次 slow（8 秒） |
| --- | --- | --- |
| 发送并成功完成 | 52 | 24 |
| 跳过发送机会 | 8 | 36 |
| Prometheus 采集到的在途峰值 | 6 | 6 |
| 服务端窗口平均耗时峰值 | 约 3.007 秒 | 约 8.010 秒 |

第二次成功速率曲线最高约 0.821 次/秒。每次模拟请求均等待约 8 秒，因此平均耗时形成约 8 秒的平台；无请求的窗口为无值，不补零。并发上限约束同时在途请求数量，不是累计完成次数；更长的等待占用并发名额更久，第二次完成数量减少、跳过机会增多。收尾后在途数量回到 0。

第二次原始截图为 `screenshots/grafana-changed-run.png`，显示实际请求速率、在途峰值与 8 秒耗时平台。仪表盘 JSON 从本次实际 Grafana 导出，保留三个 Panel 及 Prometheus 数据源变量；它只保存配置，历史数据在 Prometheus 运行数据库内，不包含在导出 JSON 中。干净环境重新运行上述两次脚本可生成新的真实曲线；提交截图记录本次实际运行。
