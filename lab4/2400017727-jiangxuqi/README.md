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
