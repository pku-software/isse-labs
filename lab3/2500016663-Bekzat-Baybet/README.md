# Lab 3 · AI 聊天助手：ACR 云端构建与 ECI 部署

- 学号：2500016663
- 姓名拼音：Bekzat Baybet
- 分支：`lab3/2500016663-Bekzat-Baybet`

## 一、项目来源与架构

本项目沿用 Lab 2 的聊天应用，功能不变；Lab 3 只解决「如何把应用连同运行环境一起打包，并以统一方式部署到云端」。

- 单个 Flask 进程（`app.py`）同时承担三件事：
  - **前端页面与静态资源**：`/` 返回 `frontend/index.html`，`/<path:filename>` 返回 `frontend/` 下的 CSS/JS；
  - **聊天记录 CRUD API**：`GET/POST /api/messages`、`PATCH/DELETE /api/messages/<id>`；
  - **健康检查**：`GET /api/hello`。
- 前端全部使用**同源相对路径**（如 `fetch("/api/messages")`），页面、静态资源与 API 由同一个容器提供，因此容器化时**无需改动任何前端代码**。
- 聊天记录只保存在进程内存中，容器重启后清空（本 Lab 不要求云端持久化）。

## 二、密钥处理方式

- 后端在**运行时**通过环境变量 `DEEPSEEK_API_KEY` 读取 Key（`os.getenv`），前端不接收、不保存、不传输 Key。
- 真实 Key 不进入源码、GitHub、Dockerfile、构建上下文、镜像、URL 与日志。
- `.env` 由 `.gitignore`（不进 Git）与 `.dockerignore`（不进镜像）双重排除；`.env.example` 仅含变量名与占位值。
- 部署时 Key 只在 ECI 的**容器运行时环境变量**中由本人手动设置。

## 三、Dockerfile 关键配置

| 配置 | 作用 |
| --- | --- |
| `FROM python:3.11-slim` | 选择官方精简 Python 基础镜像，与 Flask / requests / gunicorn 兼容 |
| `WORKDIR /app` | 设定容器内工作目录，保证 `send_from_directory("frontend", ...)` 能正确解析到 `/app/frontend` |
| `COPY requirements.txt` + `RUN pip install` | **构建阶段**安装依赖（含 gunicorn）；放在复制源码之前，源码变动时可复用缓存、不重装依赖 |
| `COPY app.py` / `COPY frontend/` | 复制应用代码与前端静态文件 |
| `EXPOSE 5001` | **仅元数据声明**，不会自动开放端口或创建公网入口 |
| `CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "--timeout", "120", "app:app"]` | **运行阶段**用 Gunicorn 启动 Flask；单 worker，监听 5001，超时 120 秒以适配模型调用 |

`.dockerignore` 排除：`.env`、`.git`、`__pycache__`、虚拟环境、`AGENT_TRACE.md`、`screenshots/`、`README.md`。

## 四、ACR 云端构建

| 项目 | 值 |
| --- | --- |
| 地域 | 华北 2（北京） |
| 实例类型 | ACR 个人版 |
| 代码源 | 个人 GitHub Fork `Bekzat070101/isse-labs` |
| 构建分支 | `lab3/2500016663-Bekzat-Baybet` |
| 构建上下文目录 | `/lab3/2500016663-Bekzat-Baybet/` |
| Dockerfile 路径 | `Dockerfile` |
| 镜像标签 | `lab3-b71b040` |
| 构建方式 | 开启海外机器构建，手动点击「立即构建」 |

镜像完整地址：（在 ECI 选择镜像时补记）

> 说明：ACR 负责**在云端构建并保存镜像**；修改代码后必须重新提交并推送，再触发一次构建，旧镜像不会自动更新。

## 五、ECI 部署

| 项目 | 值 |
| --- | --- |
| 实例 ID / 名称 | `eci-2zej4cvjxfxsdgy7sx` / `lab3-2500016663` |
| 地域 / 可用区 | 华北 2（北京）/ 可用区 H（与 ACR 同地域） |
| 付费模式 / 规格 | 按量付费、经济型，0.25 vCPU / 512 MiB |
| 镜像 | ACR 个人版（北京）镜像标签 `lab3-b71b040` |
| 启动命令 | 留空，沿用 Dockerfile 的 `CMD`（Gunicorn 监听 `0.0.0.0:5001`） |
| 环境变量 | `DEEPSEEK_API_KEY`（**值不在本文件记录**，由本人于创建时在容器运行时环境变量中设置） |
| 公网 IP | `39.96.76.139`（EIP 自动创建）；内网 IP `172.22.212.66` |
| 安全组 | 沿用默认安全组，另加一条入方向规则：自定义 TCP，端口 `5001`，授权对象 `0.0.0.0/0` |

> 排错记录：首次创建后公网访问全部超时（`Connection timed out`，而非 `Connection refused`），判断为流量在到达容器前被安全组丢弃；为 5001 端口添加放行规则后恢复。

## 六、公网访问验证

- 访问地址：`http://39.96.76.139:5001/`
- 验证结论（由 Agent 经公网实测 + 本人在浏览器实测）：

| 检查项 | 结果 |
| --- | --- |
| `GET /` | `200`，`text/html`，1182 字节 |
| `GET /style.css` | `200`，`text/css`，4698 字节 |
| `GET /app.js` | `200`，`application/javascript`，7985 字节 |
| `GET /api/hello` | `200`，`{"message":"你好"}`，响应头 `Server: gunicorn` |
| `POST /api/messages` | `201`，返回真实模型回复（验证运行时 Key 生效） |
| 浏览器实际访问 | 页面、静态资源、CRUD 与模型回复均正常 |

- 截图：`screenshots/eci-created.png`（ECI 实例创建成功）、`screenshots/public-page.png`（浏览器实际访问公网页面，含地址栏）

## 七、风险与清理计划

- 本实验使用公网 HTTP 做短时教学演示，非正式服务的安全部署方案。
- 完成 PR 后立即**删除本实验创建的 ECI 实例**，并检查、释放只为本次实验创建的 EIP 等独立计费资源。
- 实验用 DeepSeek Key 建议随后废除。
