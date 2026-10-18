# Flask 聊天应用监控

本项目基于个人 Lab 3 的 Flask 聊天应用，保留多会话、消息增删改查和原聊天接口，增加本地 mock 回复及 Prometheus 业务指标。实验请求使用固定测试文本，不调用真实模型。

## 运行环境

已验证环境为 macOS ARM64、zsh、Python 3.12.12、uv 0.10.2；应用依赖包括 Flask 3.1.3 和 prometheus-client 0.26.0。依赖范围记录于 `requirements.txt`。

在仓库根目录执行：

```sh
cd lab4/2600921006-chenhaowen
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
CHAT_MODE=mock PORT=5001 uv run --no-project --python .venv/bin/python python app.py
```

打开 `http://127.0.0.1:5001/` 使用聊天页面，打开 `http://127.0.0.1:5001/metrics` 查看指标。应用绑定本机地址，以单进程、多线程处理请求，关闭调试和自动重载。端口由 `PORT` 配置，默认是 `5001`。

`CHAT_MODE` 默认为 `mock`，只接受 `mock` 或 `real`。mock 不创建真实模型客户端，不需要 Key；`GET /api/lab-status` 返回 `{"mode":"mock","external_model_calls":false}`。原 DeepSeek 功能保留在 real 模式中，其凭据从运行环境取得，程序不会自动读取 `.env`。本实验仅运行 mock；real 模式下实验状态接口返回 404，模拟选项不参与真实模型调用。

## 聊天接口

前端使用 `POST /api/conversations/<conversation_id>/messages`；兼容接口 `POST /api/messages` 操作 ID 为 `1` 的默认会话。两个地址经过同一个处理函数，成功返回 HTTP 201 和 `id`、`message`、`reply` 字段。

mock 请求示例：

```json
{"message":"监控实验测试消息","mock_delay_seconds":0.1,"mock_force_error":false}
```

`mock_delay_seconds` 是后端等待秒数，默认 `0.1`，范围为 `0` 至 `30` 的有限数字；`mock_force_error` 必须为布尔值，默认 `false`。强制失败在等待后返回 HTTP 503，并携带 `code: "mock_failure"`。无效模拟选项返回 HTTP 400。

存储锁只保护会话的读写，后端等待时不持有锁。mock 回复不依赖历史，允许同一会话的多个回复安全追加；real 模式仍校验生成期间的历史变化，避免把基于过期上下文的回复写入会话。

## 指标

| 指标 | 类型 | 统计范围 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 两个 POST 聊天接口完成的请求，成功和错误分别累计，初始值均为 0。 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求。 |
| `chat_request_duration_seconds` | Histogram | 聊天处理的服务端耗时，包含后端等待、存储和失败路径。 |

Histogram 桶上界为 `0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 20, 30, +Inf` 秒，同时暴露 `_sum` 和 `_count`。指标模块使用独立注册表；页面、静态资源、会话管理、消息查询和编辑、状态接口、`/metrics` 访问均不增加聊天指标。指标标签不包含消息内容、会话 ID 或用户信息。

## 本地文件

mock 聊天数据写入 `.runtime/app/mock/conversations.json`，real 数据使用独立的 `.runtime/app/real/`。日志及其他运行文件位于 `.runtime/app/`；虚拟环境位于 `.venv/`；工具目录为 `.tools/`。这些目录以及 `.env`、Python 缓存均由个人 `.gitignore` 排除。

`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 来自课程 `lab4/starter/`。运行结果、仪表盘配置与截图保留在可提交的位置。

## 访问脚本适配

`simulate_traffic.py` 保留课程调度器实现，负责发送节奏、并发上限及结果统计。`project_adapter.py` 将通用动作转换为本项目的 HTTP 请求，已通过正常请求和强制失败的单请求验证并启用。

| 适配函数 | 本项目行为 |
| --- | --- |
| `confirm_mock_mode()` | GET `/api/lab-status`，要求 HTTP 200、`mode` 为 `mock` 且 `external_model_calls` 严格为布尔值 `false`；拒绝重定向和无效响应。 |
| `build_chat_request()` | POST `/api/messages`，JSON 包含 `message`、`mock_delay_seconds`、`mock_force_error`，由后端执行延迟或模拟失败。 |
| `response_is_success()` | 要求 HTTP 201、JSON 为对象、没有 `error` 字段且 `reply` 为非空字符串；HTTP 503 模拟错误及无效回复均判为失败。 |

每次运行时调度器仍会实际核验 mock 状态，未通过就退出并且不发送聊天请求。课程的本机地址限制、请求目标与根地址一致性检查、重定向限制均保留；请求不携带 Key，也不直接修改监控指标。

## 安装本地监控工具

使用官方 macOS ARM64 稳定版 [Prometheus 3.15.0](https://github.com/prometheus/prometheus/releases/tag/v3.15.0) 和 [Grafana OSS 13.2.4](https://grafana.com/grafana/download/13.2.4?edition=oss&platform=mac)。下载包与校验文件放在 `.tools/downloads/`，工具分别解压到 `.tools/prometheus/`、`.tools/grafana/`，不安装到系统目录。

在本项目目录执行以下命令；`curl -C -` 支持中断后重新执行以续传，完整校验成功后再解压。

```sh
mkdir -p .tools/downloads .tools/prometheus .tools/grafana
curl -fL --retry 2 -C - -o .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.darwin-arm64.tar.gz
curl -fL --retry 2 -C - -o .tools/downloads/grafana_13.2.4_38252365904_darwin_arm64.tar.gz https://dl.grafana.com/grafana/release/13.2.4/grafana_13.2.4_38252365904_darwin_arm64.tar.gz
printf '%s\n' '920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260  prometheus-3.15.0.darwin-arm64.tar.gz' 'a910966466359212f1d875748a72a4638c7d3724448d0c369210b31d763b165d  grafana_13.2.4_38252365904_darwin_arm64.tar.gz' > .tools/downloads/sha256sums.txt
(cd .tools/downloads && shasum -a 256 -c sha256sums.txt) && \
tar -xzf .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz --strip-components=1 -C .tools/prometheus && \
tar -xzf .tools/downloads/grafana_13.2.4_38252365904_darwin_arm64.tar.gz --strip-components=1 -C .tools/grafana
```

## 启动采集和仪表盘

保持聊天应用运行，在两个独立终端中分别执行：

```sh
zsh start-prometheus.zsh
```

```sh
zsh start-grafana.zsh
```

启动脚本会定位本项目目录，显式指定配置与数据路径。Prometheus 数据位于 `.runtime/prometheus/`；Grafana 的数据库、日志和插件分别位于 `.runtime/grafana/data/`、`.runtime/grafana/logs/`、`.runtime/grafana/plugins/`。前台运行时使用 `Ctrl+C` 停止相应进程，保留这些数据可继续查看历史。

| 程序 | 本地地址 | 用途 |
| --- | --- | --- |
| Flask | `http://127.0.0.1:5001/` | 聊天页面；`/metrics` 提供当前指标。 |
| Prometheus | `http://127.0.0.1:9090/` | 查询指标；`/targets` 显示采集状态。 |
| Grafana | `http://127.0.0.1:3000/d/lab4-chat-app` | 三个时间序列图表。 |

三者均只监听 `127.0.0.1`。Prometheus 通过 `prometheus.yml` 每 2 秒采集一次 `127.0.0.1:5001/metrics`，超时为 1 秒，job 为 `chat-app`。Target 的 `UP` 表示指标采集成功；聊天请求的结果通过 `chat_requests_total` 的 outcome 区分。

Grafana 启动时读取 `grafana/provisioning/`：数据源 `Lab 4 Prometheus` 指向 `http://127.0.0.1:9090`，UID 为 `lab4-prometheus`；仪表盘源文件为 `grafana-dashboard.json`，UID 为 `lab4-chat-app`。本机浏览器可匿名只读查看，图表每 5 秒刷新，时间按浏览器时区显示。使用这些配置启动新实例时无需重新选择数据源；单独导入仪表盘到其他实例时，先创建 UID 为 `lab4-prometheus` 的 Prometheus 数据源，或将 JSON 中的同名 UID 替换为目标数据源 UID。

| Panel | PromQL | 含义 |
| --- | --- | --- |
| 成功／失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒内平均每秒完成的请求数，按结果区分。 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 采集时刻的在途请求数。 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近 30 秒内服务端平均处理秒数。 |

Histogram 的 `_bucket{le="1.0"}` 表示耗时不超过 1 秒的累计请求数，各桶是累积的，`+Inf` 桶包含所有记录。平均耗时图使用 `_sum` 与 `_count` 的窗口增量比例，而不是桶边界。窗口内没有请求时可能显示无值；图表不补零，也不连接缺失区间。新启动的 Prometheus 需要积累多个采样点后才能计算速率。

## 模拟方法与实测结果

以下结果来自 2026-10-18 的实际 HTTP 模拟。表格时间使用 Asia/Taipei（UTC+8）；JSON 中的 `started_at`、`ended_at` 使用 UTC。每个阶段发送 30 秒，随后等待在途请求结束，因此实际起止时间可能超过 30 秒；整个脚本最后再等待 10 秒供采集器记录恢复状态。

保持应用、Prometheus 和 Grafana 运行，在本项目目录执行。下面是生成两份结果时实际使用的命令；再次运行请修改 `--output` 为新的文件名，保留本次原始结果。

```sh
uv run --no-project --python .venv/bin/python python -u simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
uv run --no-project --python .venv/bin/python python -u simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --phase-seconds 30 --slow-rate 2 --slow-delay 1 --concurrency 6 --output results/changed-run.json
```

首次完整模拟使用默认参数：baseline、errors、recovery 为每秒 1 次，burst 为每秒 4 次，slow 为每秒 2 次；通常延迟 0.1 秒，slow 延迟 3 秒；errors 中每第 3 次请求故意失败；并发上限 6、请求超时 10 秒。结果见 [first-run.json](results/first-run.json)。

| 阶段 | 实际起止时间（UTC+8） | 发送 | 成功 | 预期失败 | 跳过 | 客户端平均耗时（秒） |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 22:48:34–22:49:04 | 30 | 30 | 0 | 0 | 0.117 |
| burst | 22:49:04–22:49:34 | 120 | 120 | 0 | 0 | 0.118 |
| slow | 22:49:34–22:50:07 | 52 | 52 | 0 | 8 | 3.018 |
| errors | 22:50:07–22:50:37 | 30 | 20 | 10 | 0 | 0.118 |
| recovery | 22:50:37–22:51:07 | 30 | 30 | 0 | 0 | 0.118 |

首次共 270 次发送机会，实际发送 262 次，其中成功 252 次、预期失败 10 次、跳过 8 次；网络错误和非预期结果均为 0。成功速率在 burst 阶段升至约 4 次/秒；slow 阶段的在途数主要为 5–6，服务端平均耗时升至约 3 秒；errors 阶段出现 error 曲线，恢复阶段耗时降低、在途请求回落，错误速率随后下降。

第二次只运行 slow 场景，将后端延迟从 3 秒改成 1 秒，目标频率仍为每秒 2 次，并发上限仍为 6，持续发送 30 秒。实际时间为 23:03:46–23:04:16，共发送 60 次且全部成功，跳过、业务/HTTP 错误、网络错误和非预期结果均为 0。结果见 [changed-run.json](results/changed-run.json)。

| 对比项 | 首次 slow | 第二次 slow |
| --- | ---: | ---: |
| 后端延迟设置 | 3 秒 | 1 秒 |
| 目标频率 / 并发上限 | 2 次/秒 / 6 | 2 次/秒 / 6 |
| 发送 / 跳过 | 52 / 8 | 60 / 0 |
| Prometheus 采样到的在途峰值 | 6 | 3 |
| 服务端平均耗时曲线最高值（约） | 3.007 秒 | 1.008 秒 |
| 脚本记录的客户端平均耗时 | 3.018 秒 | 1.017 秒 |

表中的在途峰值和服务端耗时来自上述 PromQL，在两次 slow 的实际起止时间内按 2 秒步长查询。延迟缩短后，请求较快结束，同时重叠的处理减少。客户端平均耗时来自脚本 JSON，包含网络及客户端开销，与 Histogram 的服务端耗时统计范围不同。

两次 slow 都安排了 60 次发送机会；第一次达到 6 个在途请求的上限时跳过 8 次，第二次没有跳过。目标发送频率不等于实际完成频率；调度器不会在容量满时无限排队。请求速率和平均耗时采用最近 30 秒窗口，阶段切换会混合前后数据，所以图形边界平滑，停止发送后速率仍会延迟回落。Gauge 则是每 2 秒采集的一次快照；baseline 和 burst 的单次处理约 0.1 秒，即使有请求，短暂的在途峰值也可能没有被采到。

原始截图为 [Prometheus Targets](screenshots/prometheus-targets.png) 和 [完整模拟仪表盘](screenshots/grafana-dashboard.png)。仪表盘截图覆盖 22:48:24–22:51:42；第二次的观察范围为 23:03:36–23:04:51。`grafana-dashboard.json` 已从实际运行的 Grafana 导出，保留数据源 UID `lab4-prometheus`，将当前实例的数字 `id` 和修订号 `version` 分别重置为 `null`、`1` 以便导入。历史指标存放在被忽略的 Prometheus 数据库中；新环境需重新运行模拟，并选择新运行的时间范围，截图和结果 JSON 保留本次证据。

## 验证

在本项目目录执行：

```sh
uv run --no-project --python .venv/bin/python python -m unittest discover -s tests -v
uv pip check --python .venv/bin/python
node --check frontend/app.js
```

HTTP 测试使用 `.runtime/app/tests/` 下的临时应用副本和随机本地端口，结束后关闭测试服务并清理测试数据。覆盖默认 mock、禁止自动读取 `.env`、指标统计范围、模拟参数校验、并发慢请求、存储失败收尾、适配器通过原接口识别正常和强制失败请求，以及调度器拒绝 real 配置且不发送聊天请求；测试期间禁止创建外部模型客户端。适配器测试另覆盖严格状态校验、重定向拒绝及无效响应识别。
