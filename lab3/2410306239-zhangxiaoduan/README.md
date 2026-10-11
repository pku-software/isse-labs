# Lab 3：聊天应用云端部署

**姓名**：张效端　**学号**：2410306239

## 项目来源与架构

- 代码来自 Lab 2 的 Flask 聊天应用（`app.py` + `frontend/`），本 Lab 不修改应用逻辑，只负责部署。
- 架构：浏览器 → 公网 IP:5001 → ECI 容器 → Gunicorn → Flask → DeepSeek API。
- 依赖（requirements.txt）：flask、python-dotenv、openai、gunicorn。

## Dockerfile 关键配置

- 基础镜像：`python:3.11-slim`。
- 先 `COPY requirements.txt` 并安装依赖，再 `COPY` 源码——利用 Docker 分层缓存，改代码时不必重装依赖。
- `EXPOSE 5001` 仅为文档性元数据，实际监听端口由启动命令决定。
- 启动命令：`gunicorn --bind 0.0.0.0:5001 --workers 1 app:app`（单 worker 足以支撑本实验，且配合内存态会话数据）。

## ACR 云构建

- 地域：华北2（北京），个人版实例。
- 仓库：`zhangxiaoduan/lab3`（私有）。
- 代码源：GitHub 仓库 `xiaoduan-168/isse-labs`。
- 构建分支：`lab3/2410306239-zhangxiaoduan`。
- 构建上下文：`/lab3/2410306239-zhangxiaoduan/`。
- 镜像标签：`lab3-6183a2d`。
- 自动构建：关闭（按需手动触发，文档改动无需重新构建）。
- 镜像完整地址形如：`registry.cn-beijing.aliyuncs.com/zhangxiaoduan/lab3:lab3-6183a2d`。

## ECI 配置

- 地域/可用区：华北2（北京），可用区 H。
- 付费模式与规格：按量付费、普通实例、经济型算力（页面最低规格）。
- 容器组名称：`lab3-2410306239`。
- 镜像：`registry.cn-beijing.aliyuncs.com/zhangxiaoduan/lab3:lab3-6183a2d`（拉取自个人 ACR 仓库）。
- 端口：`5001`，来自 Dockerfile 中 Gunicorn 的启动命令；启动命令留空未覆盖。
- 环境变量名称：`DEEPSEEK_API_KEY`（值仅在 ECI 控制台设置，不进源码、GitHub 或镜像）。
- 弹性公网 IP：`39.106.79.72`（自动创建，按流量计费，需在实验后确认释放）。
- 安全组：创建后补充入方向规则，放行 TCP 5001（默认安全组未放行，需手动添加）。

## 公网访问验证

- 访问方式：浏览器打开 `http://39.106.79.72:5001/`。
- 验证结论：首页返回 HTTP 200；`/api/hello` 返回 `{"message":"你好"}`；静态资源 `style.css`、`app.js` 均返回 200；`GET /api/conversations` 可经公网访问（只读验证，未调用模型）；学生浏览器实际访问正常（截图见 `screenshots/public-page.png`）。

## 安全风险与清理计划

- **公网入口为 HTTP，传输不加密**：聊天内容明文经过网络，实验期间不输入敏感信息。
- **API 无鉴权**：知道公网地址的任何人可打开页面、调用聊天接口（消耗实验 DeepSeek 额度），并可经 `GET /api/conversations` 等接口读写会话记录。本方案仅为短时教学演示，不是正式服务的安全部署方式。
- **清理计划**：提交 PR 后立即删除 ECI 实例 `lab3-2410306239`，并检查自动创建的弹性公网 IP 是否仍独立计费、按需释放；实验 Key 建议随后废除；ACR 镜像与构建规则保留或按需停用。
