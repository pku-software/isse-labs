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
- 计划地域：华北 2（北京），尚未创建或验证
- 仓库、镜像标签和镜像地址：待实际构建时记录
- 学生 Push 后手动触发构建；自动构建关闭

## ECI 配置与验证进度

尚未创建 ECI，也未验证公网访问。计划使用同地域单容器，沿用 Dockerfile 启动命令；应用端口 5001，运行时变量名称 DEEPSEEK_API_KEY。规格、公网地址与实际验证结果将在操作后填写。

本地 Flask 测试客户端检查已通过：页面与静态资源、健康检查、会话与消息增删改查、空输入校验、缺少 Key 的错误处理、上游错误脱敏及无效 JSON 处理。Python 语法检查通过；`.env` 忽略规则生效且未被 Git 跟踪。测试使用临时数据目录和模拟模型回复，未读取真实 Key、未调用 DeepSeek，不代表真实模型调用或云端部署成功。尚未执行 Docker/ACR 镜像构建。

## 实验材料与清理

ECI 实例与本人浏览器公网访问的原始截图，将在实际操作后保存到 `screenshots/`。AGENT_TRACE.md 在实验末尾由学生保存真实对话或分享链接，不使用摘要替代。

提交 PR 后删除本实验 ECI，并检查、释放独立存在且仅供本实验使用的 EIP；清理状态尚未核验。
