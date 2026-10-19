# 潘勇圳的聊天应用监控实验

学号：2500093008。应用源自个人 Lab 3 Flask 聊天项目，保留前端、多会话及消息增删改查。

## 本地启动

本次环境为 macOS arm64、zsh、Python 3.12。以下命令在个人 Fork 的仓库根目录执行：

```sh
python3 -m venv lab4/2500093008-pan-yongzhen/.venv
lab4/2500093008-pan-yongzhen/.venv/bin/python -m pip install -r lab4/2500093008-pan-yongzhen/requirements.txt
MODEL_MODE=mock PORT=5001 lab4/2500093008-pan-yongzhen/.venv/bin/python lab4/2500093008-pan-yongzhen/app.py
```

应用仅监听 127.0.0.1，默认地址 http://127.0.0.1:5001/ ，单进程、多线程。会话保存在个人 `.runtime/app/conversations.json`，不提交 Git。

## 模型模式与请求

默认 `MODEL_MODE=mock`，无需 Key，不调用外部模型。`GET /api/lab/status` 返回实际 mock 状态和 `external_model_calls: false`。显式设置 `MODEL_MODE=real` 才启用原 DeepSeek 调用，所需 Key 从环境变量读取；real 模式的实验状态接口返回 404，忽略模拟选项。本实验仅使用 mock，不读取 `.env`。

前端使用 `POST /api/conversations/<id>/messages`；兼容接口 `POST /api/messages` 使用默认会话。JSON 的 `message` 为消息文本。mock 模式额外支持 `mock_delay_seconds`（0–10 秒，默认 0.1）和 `mock_force_error`（布尔值，默认 false）。成功返回 201 与 `id/message/reply`，模拟失败返回 503 与错误 JSON。延迟期间不持有存储锁。

## 应用指标

`GET /metrics` 使用 Prometheus 标准文本格式。两个聊天 POST 入口均被统计，包括参数错误与异常；页面、CRUD、状态接口及采集请求不计入聊天数量。

- `chat_requests_total{outcome="success"或"error"}`：完成的聊天处理累计次数，两种结果初始化为零。
- `chat_inprogress_requests`：正在处理的聊天请求数量，异常也会减回。
- `chat_request_duration_seconds`：服务端聊天处理耗时，包含失败；桶上界为 0.05、0.1、0.25、0.5、1、2、3、5、10、15 秒及 +Inf。

指标定义位于 `metrics.py`。开发验证请求也会计入指标，服务进程重启后内存指标重新开始。

## 本地监控工具安装与连接

使用官方 macOS ARM64 稳定版 Prometheus 3.15.0、Grafana OSS 13.2.3。下载来源分别是 [Prometheus](https://prometheus.io/download/) 与 [Grafana](https://grafana.com/grafana/download/13.2.3?edition=oss&platform=mac)。

个人目录内的固定位置：下载与校验文件 `.tools/downloads/`，程序 `.tools/prometheus/` 和 `.tools/grafana/`，Prometheus 数据 `.runtime/prometheus/`，Grafana 数据、日志、插件分别为 `.runtime/grafana/data/`、`logs/`、`plugins/`；应用数据 `.runtime/app/`，Python 环境 `.venv/`。这些目录均不提交。

从干净环境安装时，先在仓库根目录核验个人忽略规则，再在个人目录执行以下命令（首次安装，工具目录为空时）：

```sh
cd lab4/2500093008-pan-yongzhen
mkdir -p .tools/downloads .tools/prometheus .tools/grafana
curl -fL --retry 3 -o .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.darwin-arm64.tar.gz
curl -fL --retry 3 -o .tools/downloads/grafana_13.2.3_36482603486_darwin_arm64.tar.gz https://dl.grafana.com/grafana/release/13.2.3/grafana_13.2.3_36482603486_darwin_arm64.tar.gz
```

解压前用 `shasum -a 256` 核对下载包，必须与以下官方校验值一致：

| 文件 | SHA256 |
| --- | --- |
| prometheus-3.15.0.darwin-arm64.tar.gz | `920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260` |
| grafana_13.2.3_36482603486_darwin_arm64.tar.gz | `248a51bcfacdb1ec642006cee46b4de44a34bcf41ddea88d96a4605e2e9d808c` |

```sh
tar -xzf .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz --strip-components=1 -C .tools/prometheus
tar -xzf .tools/downloads/grafana_13.2.3_36482603486_darwin_arm64.tar.gz --strip-components=1 -C .tools/grafana
```

应用启动后，在两个独立终端分别运行（个人目录内）：

```sh
sh start-monitoring.sh prometheus
```

```sh
sh start-monitoring.sh grafana
```

启动脚本显式传入个人配置与运行数据目录。Prometheus 监听 `127.0.0.1:9090`，每 2 秒采集 `127.0.0.1:5001/metrics`，超时 1 秒，job 为 `chat-app`。Grafana 监听 `127.0.0.1:3000`，通过配置文件自动添加 UID 为 `lab4-prometheus` 的数据源，指向 `http://127.0.0.1:9090`，并载入 `dashboards/chat-monitoring.json`。本机匿名访问仅有 Viewer 权限，随机管理员口令保存在被忽略的 `.runtime/grafana/admin-password`，不纳入提交。

## 三个图表

仪表盘刷新间隔为 5 秒，时间范围可在页面右上角选择。查询使用最近 30 秒窗口，阶段边界会平滑，并可能存在滞后。

| Panel | PromQL | 含义 |
| --- | --- | --- |
| 成功与失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近窗口内每秒完成的成功/失败请求数，非累计次数 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前在途请求数，非在线用户数 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近窗口内服务端平均耗时，单位秒，包含失败请求 |

Histogram 的 `_bucket{le="…"}` 表示耗时不超过上界的累计请求数；`_sum` 是累计耗时，`_count` 是记录次数。第三个图使用窗口内耗时增长量除以次数增长量；没有请求时可能无值，不补零。

## 脚本适配与复现实验

`simulate_traffic.py` 为课程 starter 的原始调度器副本，未修改。`project_adapter.py` 的三个适配点分别通过 HTTP 核验 `/api/lab/status`、向原 `/api/messages` 构造 POST 请求，以及依据 201 状态与有效 `id/message/reply` 判断成功。状态检查关闭代理与重定向，核验真实返回的 mock 状态；非 mock 服务会在发送聊天请求前被拒绝。单请求验证通过后启用了 `ADAPTER_READY`。

以下命令在仓库根目录执行。首次完整运行每阶段 30 秒，并发上限 6，请求超时 10 秒，收尾等待 10 秒：

```sh
lab4/2500093008-pan-yongzhen/.venv/bin/python -u lab4/2500093008-pan-yongzhen/simulate_traffic.py --base-url http://127.0.0.1:5001 --output lab4/2500093008-pan-yongzhen/results/first-run.json
```

对照运行仅执行 slow 场景，唯一改变的请求参数为延迟 3 秒改为 5 秒，其他参数沿用默认值：

```sh
lab4/2500093008-pan-yongzhen/.venv/bin/python -u lab4/2500093008-pan-yongzhen/simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --phase-seconds 30 --slow-delay 5 --output lab4/2500093008-pan-yongzhen/results/changed-run.json
```

已有结果应保留；再次复现时请把 `--output` 改为新的文件名，避免覆盖本次真实结果。脚本只发送本机 HTTP 请求，不直接操作指标。并发容量满时跳过发送机会，阶段结束等待在途请求收尾。JSON 中的 `client_mean_seconds` 包含网络等客户端开销，不能当作服务端 Histogram。

## 实际实验结果

两次运行均在 2026 年 10 月 15 日完成。下表使用北京时间（UTC+8）；原始 JSON 保存 UTC 时间。首次完整运行无网络错误、无非预期结果，全部 10 次失败均为 errors 阶段设定的模拟失败。

| 阶段 | 北京时间 | 目标频率/秒 | 后端延迟/秒 | 发送 | 成功 | 模拟失败 | 跳过 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 01:36:07–01:36:37 | 1 | 0.1 | 30 | 30 | 0 | 0 |
| burst | 01:36:37–01:37:07 | 4 | 0.1 | 120 | 120 | 0 | 0 |
| slow | 01:37:07–01:37:39 | 2 | 3 | 52 | 52 | 0 | 8 |
| errors | 01:37:39–01:38:09 | 1 | 0.1 | 30 | 20 | 10 | 0 |
| recovery | 01:38:09–01:38:39 | 1 | 0.1 | 30 | 30 | 0 | 0 |
| 对照 slow | 08:24:40–08:25:14 | 2 | 5 | 35 | 35 | 0 | 25 |

首次累计发送 262 次，成功 252 次，模拟失败 10 次。Grafana 截图覆盖 01:35:52–01:39:24。burst 的成功速率达到约 4 req/s；slow 的在途峰值为 6，服务端平均耗时峰值约 3.008 秒；errors 的错误速率升高，recovery 后随窗口更新回落。短请求可能未被 2 秒采集间隔捕捉，因此 Gauge 短时显示 0 不表示期间没有请求。速率与平均耗时使用 30 秒窗口，变化平滑并跨越阶段边界。

对照运行无失败、无网络错误、无非预期结果。对应 08:24:25–08:25:54 窗口内，平均服务端耗时峰值约 5.010 秒，在途峰值仍为 6，成功速率峰值约 1.107 req/s，跳过次数由 8 增至 25。这反映脚本的 6 并发上限与更长处理时间限制了发送及完成速率，并非测得应用最大处理能力。客户端平均耗时分别为 3.029 秒和 5.030 秒，仅作独立客户端统计。

`results/first-run.json` 和 `results/changed-run.json` 是实际执行输出。`screenshots/prometheus-targets.png` 为学生截取的 Target UP 原图，`screenshots/grafana-dashboard.png` 为首次完整模拟的学生仪表盘原图。Target 截图显示较旧的 last scrape 页面状态，随后通过实时 API 核验采集持续正常、无错误。

## 仪表盘导入

`grafana-dashboard.json` 从实际 Grafana 仪表盘导出，包含三个 Panel，并把数据源引用转换为导入时选择的 `DS_PROMETHEUS`。在 Grafana 导入页面上传此文件，选择指向 `http://127.0.0.1:9090` 的 Prometheus 数据源即可。本项目的启动脚本则通过 provisioning 自动加载同一组查询的 `dashboards/chat-monitoring.json`，使用固定数据源 UID `lab4-prometheus`，不需要手动导入。若导入到同一实例，注意同 UID 仪表盘已存在，避免重复覆盖。

仪表盘 JSON 不包含历史指标。历史数据存放在被忽略的 `.runtime/prometheus/` 中；新环境需重新运行模拟，并在 Grafana 选择那次运行的实际时间范围。
