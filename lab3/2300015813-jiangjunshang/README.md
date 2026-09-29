# Lab 3：姜珺尚 2300015813

本项目迁移自 `lab2/姜珺尚-2300015813/`，保留 HTML/CSS/JavaScript 前端、Flask API、多会话和聊天记录 CRUD，以及按会话历史调用 DeepSeek 的行为。未迁移密钥、真实聊天数据、虚拟环境和 Lab 2 对话轨迹。

## 运行架构

Flask 的 `/` 提供首页，`/static/` 提供前端资源，前端通过同源 `/api/conversations` 及其子路径访问会话和消息。`/api/hello` 可用于非敏感连通性检查。模型请求由后端发送，运行时读取 `DEEPSEEK_API_KEY`，前端不接触 Key。应用不自动加载 `.env`；`.env.example` 仅记录变量名和占位值。

容器由 Gunicorn 单 worker 启动 `app.py` 中的 `app`，监听 `0.0.0.0:5001`，worker 超时设为 120 秒，以容纳模型请求等待。当前实现的会话列表、ID 计数器和锁都在进程内，故保持单 worker。记录运行时写入容器的 `data/conversations.json`；本实验不配置持久化存储，容器替换或删除后不保证保留数据。

## Dockerfile

基于 `python:3.12-slim`，工作目录为 `/app`。先复制并安装依赖，再复制应用与前端。`EXPOSE 5001` 声明预期端口，实际监听由 Gunicorn 的 `--bind` 决定。`CMD` 在容器启动时运行，安装依赖和复制文件发生在镜像构建阶段。

构建按顺序执行，某步失败后不会继续后续步骤，修复后需重新触发构建。未变化的前序步骤可能命中缓存，ACR 不保证断点续跑。

`.dockerignore` 使用允许列表，仅放行 Dockerfile、忽略规则、依赖清单、`app.py` 和三份前端文件。密钥文件、数据、虚拟环境、Git 元数据、截图和对话轨迹不进入构建上下文。增加运行必需文件时需同步更新允许列表和 Dockerfile。

## 本地检查

已使用 Flask 测试客户端验证首页、CSS/JavaScript、`/api/hello`、会话和消息 CRUD、无效输入、缺少 Key 时的错误处理、JSON 写入，以及模拟模型回复下的会话上下文隔离。测试使用占位 Key 和模拟 HTTP 响应，未调用真实模型，也未读取 `.env`。Python 语法与 JavaScript 语法检查通过，个人目录 `.env` 和数据目录忽略规则已核验。

本地测试不等于容器或公网验证：尚未实际构建镜像、运行 Linux Gunicorn 或验证真实模型回复，这些留待 ACR 和 ECI 阶段完成。

## ACR 与 ECI 实验记录

- 个人 Fork：`Frost-Maple/isse-labs`
- 个人分支：`lab3/2300015813-jiangjunshang`
- 计划构建上下文：`/lab3/2300015813-jiangjunshang/`
- Dockerfile：构建上下文内的 `Dockerfile`
- ACR 地域、仓库、镜像标签和构建结果：尚未操作，后续按实际结果填写。
- ECI 规格、公网地址及运行结果：尚未操作。
- 运行时变量名称：`DEEPSEEK_API_KEY`，由学生在控制台填写真实值。
- 公网浏览器验证及两张规定截图：尚未完成。
- PR 与资源清理：尚未完成；提交 PR 后由学生删除本实验 ECI 并核验相关 EIP 释放情况。

本机不要求安装 Docker；镜像构建由 ACR 完成，运行由 ECI 完成。完成代码检查和情境思考题后才进行 Commit、学生 Push 及云端构建。实验末尾由学生保存本次真实对话到 `AGENT_TRACE.md`。
