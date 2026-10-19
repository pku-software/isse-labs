# Lab 4 聊天应用监控

作者：盛仁杰（2400017748，Dranix123）。应用源自本人 Lab 3 分支 `lab3/2400017748-shengrenjie` 的提交 `7667854`，保留原前端、消息及会话 CRUD。

## 本地运行

当前环境为 macOS arm64、zsh、conda 环境 `isse-lab2`（Python 3.11.16）。干净环境需先安装 conda；若没有该环境，执行 `conda create -n isse-lab2 python=3.11 -y`。进入仓库的 `lab4/2400017748-shengrenjie/` 后运行：

```sh
conda run --no-capture-output -n isse-lab2 python -m pip install -r requirements.txt
CHAT_MODE=mock conda run --no-capture-output -n isse-lab2 python app.py
```

应用默认使用 mock，监听 `127.0.0.1:5001`，以单进程多线程处理请求。可用 `PORT` 调整端口。网页地址为 `http://127.0.0.1:5001/`，指标地址为 `http://127.0.0.1:5001/metrics`。

mock 使用固定测试回复，不创建模型客户端，不读取 `.env`。`GET /api/lab-status` 返回实际 mock 状态和 `external_model_calls: false`。聊天请求可携带 `mock_delay_seconds`（0～10 秒，默认 0.1 秒）及 `mock_force_error`（布尔值，默认 false）；强制失败等待指定延迟后返回 HTTP 503。输入无效返回 HTTP 400。

real 模式保留原 DeepSeek 功能，需显式设置 `CHAT_MODE=real` 并通过进程环境提供 `DEEPSEEK_API_KEY`；本实验不运行 real 调用。real 模式忽略 mock 参数，实验状态接口返回 404。

## 接口与存储

前端使用 `POST /api/conversations/<id>/messages`，JSON 字段为 `message`，成功返回包含 `message` 和 `reply` 的 JSON。旧接口 `POST /api/messages` 同时保留，成功返回 HTTP 201 和消息记录。

新产生的测试数据及应用日志放在 `.runtime/app/`，不提交。共享存储操作使用线程锁；模型等待期间释放存储锁，让其他请求和指标接口仍可响应。没有复制原实验聊天数据。

## 指标

`metrics.py` 定义以下指标，对两个 POST 聊天接口记录；页面、状态、采集和其他 CRUD 接口不计入聊天指标。

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 按完成结果累计，两个标签初始为零 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | Histogram | 服务端处理耗时，包含失败请求；桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、+Inf 秒 |

异常路径也记录失败和耗时，并减少在途数；标签不包含聊天内容。`/metrics` 使用 `prometheus_client` 的标准文本和内容类型，另含该库默认的进程、Python 指标。

## Prometheus 与 Grafana

选用官方稳定版 Prometheus 3.15.0 和 Grafana Enterprise 13.2.4 的 darwin-arm64 二进制包。Grafana 使用本地基础数据源和图表功能。官方来源：[Prometheus 下载](https://prometheus.io/download/)、[Grafana 下载](https://grafana.com/grafana/download?platform=mac)。

下载包和 SHA256 校验文件位于 `.tools/downloads/`；解压目录分别为 `.tools/prometheus/`、`.tools/grafana/`。下载后在 `.tools/downloads/` 执行 `LC_ALL=C LC_CTYPE=C LANG=C shasum -a 256 -c prometheus.sha256` 与 `LC_ALL=C LC_CTYPE=C LANG=C shasum -a 256 -c grafana.sha256` 验证官方摘要。工具和数据不提交，需要重新下载对应版本并解压（去掉归档最外层目录）。

在干净的 macOS arm64 环境中，可在个人目录下载并验证本次使用的版本。先用 `git check-ignore -v -- .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz .tools/downloads/grafana-enterprise_13.2.4_darwin_arm64.tar.gz .tools/prometheus/prometheus .tools/grafana/bin/grafana .runtime/prometheus/wal .runtime/grafana/data/grafana.db .runtime/grafana/log/grafana.log .runtime/grafana/plugins/test .runtime/app/app.log .venv/pyvenv.cfg` 确认各路径命中忽略规则，且 `git ls-files -- .tools .runtime .venv` 无输出，再执行：

```sh
mkdir -p .tools/downloads .tools/prometheus .tools/grafana
curl -fL --retry 2 -o .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.darwin-arm64.tar.gz
curl -fL --retry 2 -o .tools/downloads/grafana-enterprise_13.2.4_darwin_arm64.tar.gz https://dl.grafana.com/grafana-enterprise/release/13.2.4/grafana-enterprise_13.2.4_38252365904_darwin_arm64.tar.gz
```

官方 SHA256 摘要如下；可将每一行分别保存为 `.tools/downloads/prometheus.sha256` 和 `.tools/downloads/grafana.sha256`，再进入下载目录运行上文的校验命令，两项都为 `OK` 后解压。

```text
920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260  prometheus-3.15.0.darwin-arm64.tar.gz
15d92dc7dd6d5f9599fa2822d1e83acb45e2c03a77694d7871330341c14d6250  grafana-enterprise_13.2.4_darwin_arm64.tar.gz
```

回到个人目录后执行：

```sh
LC_ALL=C LC_CTYPE=C LANG=C tar -xzf .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz -C .tools/prometheus --strip-components=1
LC_ALL=C LC_CTYPE=C LANG=C tar -xzf .tools/downloads/grafana-enterprise_13.2.4_darwin_arm64.tar.gz -C .tools/grafana --strip-components=1
```

应用启动后，在本目录两个终端分别执行：

```sh
zsh start-monitoring.sh prometheus
```

```sh
zsh start-monitoring.sh grafana
```

Prometheus 监听 `127.0.0.1:9090`，配置为 `prometheus.yml`，采集 `127.0.0.1:5001/metrics`，job 为 `chat-app`，间隔 2 秒、超时 1 秒。数据库显式存放在 `.runtime/prometheus/`。

Grafana 监听 `127.0.0.1:3000`，使用 `grafana.ini`，数据、日志、插件分别存放于 `.runtime/grafana/data/`、`log/`、`plugins/`。本地允许匿名 Viewer 查看仪表盘。`grafana-provisioning/` 自动配置数据源 `Lab4 Prometheus`（UID `lab4-prometheus`，URL `http://127.0.0.1:9090`），并从运行目录加载 `grafana-dashboard.json` 的副本。浏览器访问 `http://127.0.0.1:3000/d/lab4-chat`。启动脚本会复制当前仪表盘文件到运行目录，便于再次启动时加载。

仪表盘每 5 秒刷新，三个时间序列 Panel 的查询为：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
sum(chat_inprogress_requests{job="chat-app"})
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

它们依次表示最近 30 秒的成功/失败平均完成速率、采集时刻正在处理的请求数、最近 30 秒包含失败请求的服务端平均耗时。没有新请求时耗时可能无值，仪表盘保留空缺。手动导入仪表盘时，先建立 UID 为 `lab4-prometheus` 的 Prometheus 数据源；或把 JSON 中的 UID 改为已有数据源的 UID，再导入。

## 课程访问脚本适配

`simulate_traffic.py` 保持课程原样，负责发送节奏、有限并发、阶段切换与真实结果统计。`project_adapter.py` 将这些通用操作转换成原项目 HTTP 请求：

- `confirm_mock_mode()` 禁止重定向，通过 `GET /api/lab-status` 核验 `mode=mock` 且 `external_model_calls=false`，随后通过 `POST /api/conversations` 创建本次测试会话并保存其 ID；状态不符或请求失败则拒绝运行。
- `build_chat_request()` 访问 `POST /api/conversations/<id>/messages`，发送 `message`、`mock_delay_seconds`、`mock_force_error`，不携带模型 Key。
- `response_is_success()` 要求 HTTP 200、JSON 含非空回复和消息字段且没有错误；模拟 HTTP 503 判为失败，无效 JSON 也判为失败，不打印聊天正文。

模拟脚本只访问本机，延迟与失败在后端执行。会话创建不计入聊天指标；只有聊天处理完成时记录成功/失败次数和耗时。

## 实际模拟与复现

两次运行日期均为 2026-10-15；下表为北京时间（Asia/Shanghai），结果 JSON 使用 UTC。应用和监控工具启动后，在个人目录执行以下命令。结果路径需要保留原始记录时请另选文件，避免覆盖已提交结果。

首次完整模拟：

```sh
conda run --no-capture-output -n isse-lab2 python -u simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
```

默认五阶段各调度 30 秒，单请求超时 10 秒，并发上限 6，末尾等待采集 10 秒；各阶段会等待在途请求收尾。实际结果：

| 阶段 | 实际开始—结束 | 目标频率（次/秒） | 后端延迟（秒） | 发送 | 成功 | 业务/HTTP 失败 | 跳过 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 12:48:14—12:48:44 | 1 | 0.1 | 30 | 30 | 0 | 0 |
| burst | 12:48:44—12:49:14 | 4 | 0.1 | 120 | 120 | 0 | 0 |
| slow | 12:49:14—12:49:46 | 2 | 3 | 52 | 52 | 0 | 8 |
| errors | 12:49:46—12:50:16 | 1 | 0.1 | 30 | 20 | 10 | 0 |
| recovery | 12:50:16—12:50:46 | 1 | 0.1 | 30 | 30 | 0 | 0 |

总计发送 262 次，成功 252 次、预期模拟失败 10 次；没有网络错误或非预期结果。errors 阶段每第 3 次请求强制失败。Prometheus 采集数据显示：成功速率峰值约 4 次/秒，在途数最高 6，平均服务端耗时最高约 3.006 秒。慢回复阶段在途数和平均耗时上升，恢复阶段随后回落。速率与平均耗时使用 30 秒窗口，因此阶段边界会平滑、恢复会有滞后；短请求的在途峰值可能被 2 秒采集间隔漏掉。首次 slow 阶段同时改变频率和延迟，不能将速率变化全部归因于延迟。

第二次仅运行 slow 场景，只把目标频率从 2 改为 4 次/秒；延迟保持 3 秒，并发上限保持 6：

```sh
conda run --no-capture-output -n isse-lab2 python -u simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --slow-rate 4 --phase-seconds 30 --output results/changed-run.json
```

实际阶段为 13:06:56—13:07:29。30 秒内安排 120 次发送机会，发送 57 次且全部成功，跳过 63 次，没有网络错误或非预期结果。

与第一次 slow 的发送 52 次、跳过 8 次相比，提高目标频率后发送量仅增至 57 次，跳过增至 63 次。实际完成速率的 30 秒窗口峰值约 1.893 次/秒，在途数最高仍为 6，服务端平均耗时峰值约 3.007 秒。并发上限 6 和单次约 3 秒的处理时间将持续处理能力限制在约每秒 2 次；目标频率不等于实际完成频率。跳过的发送机会未产生 HTTP 聊天请求，不计入应用指标。

JSON 中的 `client_mean_seconds` 包含 HTTP 和网络开销，不能当作服务端 Histogram；两次 slow 的客户端平均耗时分别约 3.0073 秒和 3.0079 秒。服务端耗时数值来自 Prometheus 的 Histogram 查询。

## 截图与查看范围

以下均为学生浏览器截图原始 PNG：

- `screenshots/prometheus-targets.png`：`chat-app`，`127.0.0.1:5001/metrics` 为 UP。
- `screenshots/prometheus-query.png`：累计请求数查询。
- `screenshots/grafana-dashboard.png` 与 `screenshots/grafana-duration.png`：同一次完整模拟的图表，前者包含请求速率和在途数，后者补充平均耗时；合起来覆盖三个 Panel。

首次图表时间范围为 12:48:00—12:51:30；第二次比较范围为 13:06:40—13:08:30。可在 Grafana 时间选择器中输入相应日期和时间。监控数据库不随代码提交，干净环境需要重新执行模拟并选择新运行的时间范围，不能只导入仪表盘就取得旧历史曲线。`grafana-dashboard.json` 从本次实际运行的 Grafana 导出，保留数据源 UID 引用，移除实例内数字 ID 以便导入。
