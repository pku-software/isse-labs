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

`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 来自课程 `lab4/starter/`。调度器保留课程实现；`project_adapter.py` 是项目 HTTP 适配入口，只有完成适配并通过单请求验证后才能启用。运行结果、仪表盘配置与截图保留在可提交的位置。

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

## 验证

在本项目目录执行：

```sh
uv run --no-project --python .venv/bin/python python -m unittest discover -s tests -v
uv pip check --python .venv/bin/python
node --check frontend/app.js
```

HTTP 测试使用 `.runtime/app/tests/` 下的临时应用副本和随机本地端口，结束后关闭测试服务并清理测试数据。覆盖默认 mock、禁止自动读取 `.env`、指标统计范围、模拟参数校验、并发慢请求、存储失败收尾及 real 配置无法报告 mock；测试期间禁止创建外部模型客户端。
