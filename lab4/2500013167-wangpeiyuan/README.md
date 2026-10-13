# Lab 4：本地聊天应用监控

王珮源，2500013167。应用来源为个人 Lab 3 Flask 项目，保留 HTML/CSS/JavaScript 前端与内存聊天记录 CRUD。

## Windows 本地运行

在本目录执行：

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
./start-app.ps1
```

页面为 http://127.0.0.1:5001/，指标为 http://127.0.0.1:5001/metrics。启动脚本明确设置 `MODEL_MODE=mock`，单进程线程并发，无重载器。可用 `./start-app.ps1 -Port 5002` 更换端口。

`POST /api/messages` 接收 `message`。mock 模式返回固定测试回复，可选 `mock_delay_seconds`（0～30 秒有限数值）和 `mock_force_error`（布尔值）；模拟失败返回 HTTP 503。`GET /api/lab-status` 仅在 mock 模式提供，返回实际模式及 `external_model_calls=false`。mock 路径不读取 Key、不调用外部模型。聊天记录仅在内存中，重启清空，读写使用线程锁。

保留 `MODEL_MODE=real` 功能，需自行配置后端环境变量 `DEEPSEEK_API_KEY`；real 模式忽略模拟选项。本实验使用 mock。应用不加载 `.env`。

## 指标

仅聊天创建请求记录业务指标；静态资源、读取/修改/删除记录、状态和采集请求均不计入。

- `chat_requests_total{outcome="success"或"error"}`：处理完成后累计，两种结果初始化为零。
- `chat_inprogress_requests`：处理开始增加，所有结束路径减少。
- `chat_request_duration_seconds`：服务端处理耗时，含失败；桶覆盖 0.05～30 秒，并暴露总和与次数。

HTTP 验证通过首页、mock 状态、创建/修改/删除、一次模拟失败及慢请求期间指标响应。三次聊天测试产生成功 2、失败 1，结束后在途为 0，耗时样本数为 3。慢请求等待 2 秒期间，指标接口约 0.025 秒响应；再次运行会继续累加，时延随环境变化。

工具、运行数据和虚拟环境分别保存在本目录 `.tools/`、`.runtime/`、`.venv/`，均不提交。

## Prometheus 与 Grafana

Windows x64 官方稳定版本：Prometheus 3.15.0（2026-09-24）、Grafana OSS 13.2.3（2026-09-29）。安装包和官方 SHA256 记录放在 `.tools/downloads/`；校验后将包内顶层目录的内容分别解压到 `.tools/prometheus/`、`.tools/grafana/`。

应用启动后在个人目录执行 `./start-monitoring.ps1`。Prometheus 启动参数为 `--config.file=<个人目录>/prometheus.yml --storage.tsdb.path=<个人目录>/.runtime/prometheus --web.listen-address=127.0.0.1:9090`，每 2 秒采集 `127.0.0.1:5001/metrics`，超时 1 秒。Targets 页面为 http://127.0.0.1:9090/targets。

Grafana 启动命令为 `.tools/grafana/bin/grafana.exe server --homepath=<个人目录>/.tools/grafana --config=<个人目录>/grafana.ini`。脚本将 `GF_PATHS_DATA`、`GF_PATHS_LOGS`、`GF_PATHS_PLUGINS` 分别设为 `.runtime/grafana/data`、`logs`、`plugins`；`GF_PATHS_PROVISIONING` 指向个人 `grafana/provisioning/`。数据源为 `http://127.0.0.1:9090`，UID 为 `lab4-prometheus`。启动脚本将仪表盘复制到 `.runtime/grafana/dashboards/`，并设置 provisioning 使用该目录。

Grafana 仅监听 `127.0.0.1:3000`，允许本机匿名 Viewer 查看仪表盘，刷新为 2 秒。页面为 http://127.0.0.1:3000/d/lab4-wangpeiyuan/ 。配置内包含三个查询：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
sum(chat_inprogress_requests{job="chat-app"})
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

分别表示最近 30 秒内平均每秒完成的请求数（成功/失败分组）、当前在途聊天请求数、最近 30 秒内平均服务端处理秒数。无请求时平均耗时可能无值，不填充假零值。Histogram 的 `_bucket{le="..."}` 是耗时不超过该上界的累计次数，`_sum` 是耗时总和，`_count` 是样本数。

仪表盘引用数据源 UID `lab4-prometheus`；重新部署可沿用 provisioning，手工导入时须先创建相同 UID 的 Prometheus 数据源或调整仪表盘引用。更换端口时同步修改采集配置、数据源与监听配置。
