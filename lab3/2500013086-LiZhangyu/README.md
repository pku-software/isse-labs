# Lab 3：将 Flask 聊天应用部署到云端

姓名：李彰宇
学号：2500013086

## 项目说明

本项目沿用 Lab 2 的 HTML、CSS、JavaScript 与 Flask 聊天应用。Flask 在同一服务中提供网页、静态资源和会话 API；前端通过同源相对路径访问 API。应用运行时从后端环境变量 `DEEPSEEK_API_KEY` 读取实验 Key，真实 Key 不进入源码、镜像或 Git 仓库。

会话数据只保存在容器本地文件中，本实验不配置云端持久化存储。

## 容器运行

ACR 根据本目录的 `Dockerfile` 在云端构建镜像。容器启动时由 Gunicorn 使用单 worker 在 `0.0.0.0:5001` 监听请求，并加载 `app.py` 中的 Flask `app` 对象。

## ACR 构建记录

ACR 个人版与后续 ECI 均使用华北 2（北京）地域。

- ACR 镜像命名空间：`lab3-chat`
- ACR 镜像仓库：`lab3-chat`
- GitHub 代码仓库：个人 Fork `lzy796/isse-labs`
- 构建分支：`lab3/2500013086-LiZhangyu`
- 构建上下文：`/lab3/2500013086-LiZhangyu/`
- Dockerfile：个人目录中的 `Dockerfile`
- 镜像标签：`lab3-4725134`
- 构建方式：关闭自动构建，使用海外机器云端手动构建

ACR 已成功从上述个人 GitHub 分支构建并保存镜像。本地代码更新后，需要先提交并 Push 到该个人分支，再触发新的 ACR 构建。

## ECI 配置与访问验证

- 地域：华北 2（北京），与 ACR 相同
- 容器组名称：`lab3-2500013086`
- 实例类型：按量付费普通实例，经济型，2 vCPU / 4 GiB
- 镜像：ACR 私有仓库 `lab3-chat/lab3-chat:lab3-4725134`
- 启动方式：沿用 Dockerfile 的 `CMD`，由 Gunicorn 单 worker 监听 `0.0.0.0:5001`
- 运行时环境变量名称：`DEEPSEEK_API_KEY`（真实值未写入源码、镜像、文档或截图）
- 公网入口：自动创建 EIP，安全组仅为实验临时放行 TCP `5001`
- 验证地址：`http://47.94.198.31:5001/`

公网检查确认首页、`app.js`、`/api/hello` 和会话列表均返回 HTTP 200。学生浏览器进一步确认页面与样式正常加载、会话创建成功，并使用非敏感内容取得一次模型回复。`screenshots/eci-created.png` 记录 ECI 容器运行状态，`screenshots/public-page.png` 记录带公网地址栏的实际应用页面。

本次实际请求链路为：浏览器访问 EIP 的 5001 端口，安全组允许 TCP 5001 后，请求进入 ECI 容器网络，由监听 `0.0.0.0:5001` 的 Gunicorn 接收并转交 Flask 路由处理。无需 DNS、SLB 或额外端口转换。

## 安全与清理

真实 Key 仅在 ECI 运行时通过环境变量设置。当前演示使用 HTTP，聊天内容在传输中未加密；API 没有鉴权，知道公网地址的人可能访问会话接口或调用模型，造成数据与额度风险。因此只使用非敏感测试内容，不将本部署作为正式服务。

完成实验、提交 PR 后，将删除本实验创建的 ECI，并核对自动创建的 EIP 是否仍作为独立资源存在和计费；若只用于本实验，也会将其释放。实验 Key 随后建议废除。
