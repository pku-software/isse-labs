# Lab 4 聊天应用监控

作者：盛仁杰（2400017748，Dranix123）。应用源自本人 Lab 3 分支 `lab3/2400017748-shengrenjie` 的提交 `7667854`，保留原前端、消息及会话 CRUD。

## 本地运行

当前环境为 macOS arm64、zsh、conda 环境 `isse-lab2`（Python 3.11.16）。在本目录运行：

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
