# Lab 3：陈川泽 2300017804

沿用 Lab 2 的 Flask 与 HTML/CSS/JavaScript 聊天应用，保留会话和消息 CRUD、多轮聊天及 DeepSeek 后端调用。

## 应用与镜像

- Flask 同时提供 `/` 页面、`/frontend/` 静态资源和 `/api/` 接口；前端使用同源相对路径。
- 后端在运行时读取 `DEEPSEEK_API_KEY`。真实 Key 只由学生在 ECI 容器环境变量中设置，不进入 Git、构建参数或镜像。
- Dockerfile 使用 `python:3.12-slim`，工作目录为 `/app`；先复制依赖清单并安装，再复制应用。
- Gunicorn 导入 `app.py` 中的 `app` 对象，单 worker 监听 `0.0.0.0:5001`，worker 超时为 180 秒，为模型响应留出等待时间。导入应用不会执行 `if __name__ == "__main__"` 内的 Flask debug 启动代码。
- 单 worker 与现有进程内会话状态保持一致；本实验不提供高并发能力。
- `EXPOSE 5001` 记录预期端口，不会自动开放公网。
- `.dockerignore` 排除 `.env*`、虚拟环境、缓存、聊天数据、截图、轨迹、项目说明和测试文件；`.gitignore` 忽略凭据及运行数据，保留只有占位值的 `.env.example`。
- 聊天数据写入容器内 `data/conversations.json`，没有挂载持久化存储；容器被替换或删除后不保证保留。

## 本地非敏感检查

使用安装了 `requirements.txt` 依赖的 Python，在本目录运行：

```text
python -B -m unittest -v test_app
```

测试使用模拟模型回复和自动清理的测试目录，不读取 `.env`，不调用真实 DeepSeek。

2026-10-09 本地验证：4 项测试通过（页面与静态资源、输入校验与缺失 Key、会话和多轮消息 CRUD、原单消息 CRUD）；JavaScript 语法和 Gunicorn 配置检查通过。实际启动 Gunicorn 后，首页、静态资源、`/api/hello`、`/api/conversations` 均返回 HTTP 200，测试服务随后停止。`.env` 与运行数据的 Git 忽略规则已核对，凭据文件未被跟踪。

本地检查使用 macOS/Python 3.13，不等同于 Linux/Python 3.12 镜像构建验证；未调用真实模型。ACR 构建及学生浏览器验证结果见下文。

## ACR 云端构建

代码源为个人 Fork `GG-booond/isse-labs`，分支为 `lab3/2300017804-ChenChuanze`，构建上下文为 `/lab3/2300017804-ChenChuanze/`，Dockerfile 位于该上下文中的 `Dockerfile`。

- 地域：华北 2（北京），`cn-beijing`；个人版私有镜像仓库。
- ACR 命名空间：`lab3-2300017804`；镜像仓库：`chat-app`。
- 构建规则：Branch，分支及上下文同上；Dockerfile 文件名为 `Dockerfile`。
- 海外机器构建开启，自动构建关闭，其他选项保持默认。
- 镜像标签：`lab3-89a96ec`，对应代码提交 `89a96ec7d09904097270d72125e26da9eff7bd49`。
- 2026-10-09：Agent 核对 GitHub 远端分支与代码提交一致；学生按上述设置操作 ACR，并报告控制台显示构建成功。
- 实际使用的镜像地址见下文 ECI 配置。

代码须先 Commit、Push，再触发 ACR 构建；ACR 无法读取仅保留在本机的新提交。本次后续 README 文档更新不需要重新构建镜像。

## ECI 配置与访问验证

ECI 与 ACR 使用同一地域；沿用镜像中的启动命令，应用实际端口为 `5001`，环境变量名称为 `DEEPSEEK_API_KEY`。

- 实例名称：`lab3-2300017804`；实例 ID：`eci-2ze898e4tf6kucndfh1e`。
- 地域：华北 2（北京），可用区 I；按量付费、普通实例、经济型，0.25 vCPU / 512 MiB 内存，单容器。
- 镜像：`crpi-tv9u3h9mrjdqboyz-vpc.cn-beijing.personal.cr.aliyuncs.com/lab3-2300017804/chat-app:lab3-89a96ec`。
- 环境变量名称：`DEEPSEEK_API_KEY`，值由学生在控制台亲自填写；启动命令留空，使用镜像 CMD；应用监听 `5001/TCP`。
- 使用默认 VPC、交换机和默认安全组；交换机 ID 为 `vsw-2zetfclzc9shkjefid0gi`，安全组 ID 为 `sg-2ze3a7oba5ag57gnmk3i`。
- 自动创建 EIP，ID 为 `eip-2zelbjrofvivfw4zgf62n`，名称为 `auto-create-for-eci-2ze898e4tf6kucndfh1e`；公网地址为 `http://39.106.120.1:5001/`，带宽峰值 1 Mbps，BGP（多线），按使用流量计费，流量由 CDT 结算。控制台已核对为“已分配”，绑定本次 ECI。
- 创建前页面展示 ECI 计算费用为 0.00000982 元/秒（约 0.0354 元/小时），不含 EIP；EIP 保有费及实际出网流量另计，模型调用也消耗实验额度。
- 学生明确确认按量费用、服务协议，以及创建默认 ECI 服务关联角色后，由 Agent 操作创建。2026-10-09 17:13:02 创建，控制台已核对为“运行中”。
- Agent 实际公网检查：首页、JavaScript、CSS、`/api/hello`、`/api/conversations` 均返回 HTTP 200；使用非敏感消息取得真实模型回复“部署成功”，并验证会话重命名、消息修改和删除、会话删除。任务创建的临时会话已删除。
- 学生此前已亲自在 Chrome 访问公网网页并进行非敏感聊天。原始截图中地址栏为 `39.106.120.1:5001`，页面实际加载，会话中显示“1+1等于几”的模型回复；历史原图在本地保留为 `public-page-2026-10-09.png`，核看未含凭据，不作为本次新实例的提交截图。
- 2026-10-09 后续排查：控制台显示该实例为“已过期（Expired）”，操作请求返回 `IncorrectStatus`；原公网地址已无法响应。事件页仍保留镜像成功拉取、容器于 17:13:33 正常启动的记录，没有提供过期原因。上述运行中与访问验证描述为此前结果，不代表当前仍在运行。
- 2026-10-10 学生重新创建实例 `eci-2zeeehnwopu32v6ns5ab`，名称 `lab3-2300017804-retry`。Agent 在实例列表核对其创建时间为 16:51:09，状态为运行中，经济型 0.25 vCPU / 512 MiB，北京可用区 I，沿用上述安全组和交换机；私网 IP 为 `172.20.75.84`。
- 学生另行创建 EIP `eip-2zeeg96bb0x9r96ivqc2i`，名称 `lab3-2300017804-eip`，创建时间为 2026-10-10 17:05:31。完成本人身份验证后，控制台核对其已分配，以普通 NAT 模式绑定当前 ECI 的网卡 `eni-2zec6datjniuyo7hes6s`。公网地址恰好仍为 `http://39.106.120.1:5001/`；北京、BGP（多线）、1 Mbps、按量付费、按使用流量计费，由 CDT 结算。购买页展示公网 IP 保有费 0.02 元/小时，出网流量另计。
- 新实例公网验证：首页、实际引用的 `/frontend/app.js` 和 `/frontend/style.css`、`/api/hello`、`/api/conversations` 均返回 HTTP 200，浏览器实际渲染页面。临时会话取得真实模型回复“公网部署成功”，会话重命名、消息修改、消息删除、会话删除均成功，测试会话已清理。
- 学生本次提供的原始截图已核看并保持原始字节：`screenshots/eci-created.png` 显示 `lab3-2300017804-retry` 运行中；`screenshots/public-page.png` 包含地址栏 `39.106.120.1:5001` 和“你好”的实际模型回复。两图可打开、未含凭据。学生随后明确确认已亲自测试会话重命名、消息修改和删除；上述 Agent 公网检查也验证了对应接口成功。
- ECI 列表仍仅列出新实例的私网 IP；本次公网入口是在 EIP 控制台绑定网卡，绑定状态以该页面核对的资源 ID 为准。旧 Expired 实例行仍显示同一公网地址的历史记录，不表示新 EIP 绑定到了旧实例。

两张必交原始截图已保存为 `screenshots/eci-created.png` 与 `screenshots/public-page.png`。学生亲自运行本地会话导出命令，将真实用户与助手对话原文保存至 `AGENT_TRACE.md`；Agent 核对 109 条对话与本地记录逐字一致，未发现所检查的凭据格式。轨迹不含系统提示、内部推理、工具日志和图片数据，不是生成的摘要。

本实验短时使用公网 HTTP，浏览器与 ECI 之间的聊天内容不加密，不输入敏感信息。Key 留在后端，不随前端请求传输；聊天 API 没有鉴权，知道公网地址的人可能调用模型并消耗实验额度。ECI 即使无人访问也可能持续计费，创建前由学生核对控制台展示的 ECI 和 EIP 实际价格。

## 资源清理

本实验旧 ECI `eci-2ze898e4tf6kucndfh1e` 已进入 Expired 终态；此前华北 2（北京）EIP 控制台按原公网 IP 查询后未列出资源，原关联 EIP `eip-2zelbjrofvivfw4zgf62n` 未保留。实例列表仍显示终态元数据，不能将其描述为已手动删除。费用控制台页面加载失败，未核实账户余额、欠费原因或最终账单；停止产生新费用不代表历史费用已结清。新实例 `eci-2zeeehnwopu32v6ns5ab` 和独立 EIP `eip-2zeeg96bb0x9r96ivqc2i` 尚未释放。PR 提交后须删除新 ECI，并单独核对、释放本次另购的 EIP，不能假定删除 ECI 会自动释放它；不要仅凭公网 IP 判断新旧资源，须核对资源 ID。建议随后废除实验 Key。默认 VPC、交换机、安全组和 ECI 服务关联角色不作为计费实例删除，不清理其他资源。
