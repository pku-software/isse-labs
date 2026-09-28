# Lab 3：ACR 构建与 ECI 部署

姓名：潘勇圳；学号：2500093008。

## 项目与架构

沿用本人 Lab 2 的 Flask + HTML/CSS/JavaScript 聊天应用，保留会话管理和消息增删改查。Flask 同时提供 `/` 页面、前端静态资源及 `/api` 接口；前端使用同源相对路径。`/api/hello` 用于非敏感健康检查。

GitHub 个人 Fork `Yongzhen23/isse-labs` 保存源码；ACR 根据 Dockerfile 在云端构建并保存镜像；ECI 拉取镜像，使用 Gunicorn 运行 Flask。DEEPSEEK_API_KEY 只在容器运行时由学生注入，前端不接收 Key。应用不自动读取 `.env`；`.env.example` 仅说明变量名称。

## Dockerfile

基础环境为 Python 3.12 slim，工作目录 `/app`。先复制依赖清单并安装依赖，再复制应用和前端，便于构建器复用未变化的依赖层。启动入口 `app:app`，单个同步 worker 监听 `0.0.0.0:5001`；Gunicorn 超时 120 秒，为后端模型请求留出时间。`EXPOSE 5001` 是端口说明，不会自动开放公网入口。

镜像只复制依赖清单、app.py 和 frontend。`.dockerignore` 还排除环境文件、虚拟环境、聊天数据、缓存、日志、截图和对话轨迹。构建阶段不需要 Key。

数据保存在内存及容器内 `data/conversations.json`，采用单 worker 避免多个进程各自维护不同会话状态。本实验不配置持久化存储，替换或释放容器可能丢失聊天记录。

## ACR 构建配置

- 个人分支：`lab3/2500093008-PanYongzhen`
- 构建上下文：`/lab3/2500093008-PanYongzhen/`
- Dockerfile：上下文内的 `Dockerfile`（按控制台字段要求填写）
- 地域：华北 2（北京）
- ACR 命名空间：`yongzhen23-lab3`
- 镜像仓库：`lab3-chat`（私有）
- 镜像标签：`lab3-997873f`
- 镜像地址：`crpi-5dewksocq9l0lctp.cn-beijing.personal.cr.aliyuncs.com/yongzhen23-lab3/lab3-chat:lab3-997873f`
- 学生 Push 后手动触发构建；自动构建关闭

ACR 已从个人 GitHub Fork 的上述分支完成云端构建，构建成功，耗时 27 秒。海外机器构建开启，构建缓存未禁用。

## ECI 配置与验证进度

已在华北 2（北京）创建按量付费的普通 ECI 实例：

- 实例 ID：`eci-2ze2xs0la9bavlb6m2kp`
- 算力类别与规格：经济型，0.25 vCPU、512 MiB
- 可用区：北京可用区 I
- 容器：单容器，使用镜像 `lab3-chat:lab3-997873f`
- 启动方式：未覆盖镜像启动命令，沿用 Dockerfile 中的 Gunicorn `CMD`
- 应用监听：`0.0.0.0:5001`
- 运行时环境变量名称：`DEEPSEEK_API_KEY`；值未进入代码、镜像、文档或截图
- 公网 IP：`39.106.178.102`，自动创建 EIP
- 安全组：允许公网 IPv4 访问 TCP `5001/5001`

公网验证通过：`GET /`、`GET /style.css`、`GET /app.js`、`GET /api/hello` 和 `GET /api/conversations` 均返回 HTTP 200；浏览器实际加载页面，并使用非敏感测试内容取得一次 DeepSeek 回复。浏览器截图中的地址栏为 `http://39.106.178.102:5001`。

当前公网入口使用 HTTP，聊天内容未加密；聊天 API 没有鉴权，知道公网地址的人可能调用接口并消耗模型额度。该部署仅用于短时教学演示。

本地 Flask 测试客户端检查已通过：页面与静态资源、健康检查、会话与消息增删改查、空输入校验、缺少 Key 的错误处理、上游错误脱敏及无效 JSON 处理。Python 语法检查通过；`.env` 忽略规则生效且未被 Git 跟踪。测试使用临时数据目录和模拟模型回复，未读取真实 Key、未调用 DeepSeek，不代表真实模型调用或云端部署成功。尚未执行 Docker/ACR 镜像构建。

## 实验材料与清理

两张原始 PNG 截图已保存到 `screenshots/eci-created.png` 和 `screenshots/public-page.png`。前者显示 ECI 实例运行中，后者显示公网地址栏、已加载页面及非敏感模型回复。AGENT_TRACE.md 在实验末尾由学生保存真实对话或分享链接，不使用摘要替代。

提交 PR 后删除本实验 ECI，并检查、释放独立存在且仅供本实验使用的 EIP；清理状态尚未核验。
