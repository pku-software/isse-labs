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

本机安装依赖时，已有 SOCKS 代理设置使新虚拟环境的 pip 安装失败；以上命令仅对安装进程移除代理变量并使用官方 PyPI，不修改系统代理配置。实际安装版本为 Flask 3.1.3、prometheus-client 0.26.0、OpenAI 3.29.0。

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
