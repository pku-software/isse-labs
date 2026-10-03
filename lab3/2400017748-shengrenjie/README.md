# Lab 3：AI 聊天助手云端部署

盛仁杰（2400017748）的 Lab 3 项目，沿用 Lab 2 的 Flask 与原生 HTML/CSS/JavaScript 聊天应用。Flask 提供页面、静态资源及会话和消息 API；前端使用同源相对路径调用 API。后端在运行时从 `DEEPSEEK_API_KEY` 环境变量读取实验 Key。

## 容器构建与运行

ACR 从个人 GitHub Fork 的 `lab3/2400017748-shengrenjie` 分支，以 `/lab3/2400017748-shengrenjie/` 为构建上下文，按本目录的 `Dockerfile` 在云端构建镜像。本地无需 Docker。镜像运行时，Gunicorn 使用单 worker 监听 `0.0.0.0:5001`，由同一 Flask 容器提供页面、静态资源及 API。`EXPOSE 5001` 记录预期端口；公网访问仍取决于 ECI 的网络配置。

`.dockerignore` 排除本地环境变量文件、聊天数据、对话轨迹、截图和缓存。真实 Key 只由本人在 ECI 容器运行时设置为环境变量，不进入源码、GitHub 或镜像。聊天数据写入容器内 `data/`，本实验不提供云端持久化。

## ACR 构建记录

- 地域：华北 2（北京）
- 私有镜像仓库：`isse-lab/isse-lab`
- 代码源：个人 GitHub Fork `Dranix123/isse-labs`
- 构建分支：`lab3/2400017748-shengrenjie`
- 构建上下文：`/lab3/2400017748-shengrenjie/`
- Dockerfile 文件名：`Dockerfile`
- 镜像标签：`lab3-ad3ad7e`
- 构建 ID：`7c2f6eb8-70e8-4183-8409-0316070b9e94`；ACR 构建页显示成功

## ECI 实验记录

- 地域：华北 2（北京），北京可用区 H；按量付费、经济型，0.25 vCPU / 0.5 GiB
- 实例 ID：`eci-2zedish0bzjikrugpqhh`；容器组名称：`container-group-1791011410248`
- 镜像：`isse-lab/isse-lab:lab3-ad3ad7e`；Gunicorn 监听 TCP 5001
- 运行时环境变量名称：`DEEPSEEK_API_KEY`，由本人在 ECI 控制台设置，值不记录
- 公网 IP：`182.92.0.189`；访问地址：`http://182.92.0.189:5001/`
- 实例截图：`screenshots/eci-created.png`
- Agent 从公网检查：首页、`/style.css`、`/app.js`、`/api/hello`、`/api/conversations` 均返回 HTTP 200
- 学生用浏览器访问上述公网地址，验证页面、会话操作，并用非敏感内容获得一次模型回复；浏览器原始截图见 `screenshots/public-page.png`

## 公网使用与资源清理

本实验入口使用 HTTP，浏览器发送的聊天内容未加密，不输入敏感信息。聊天 API 未设置鉴权，知道公网地址的人可能访问聊天内容或调用模型，消耗实验额度。实验 Key 保存在 ECI 容器运行时环境变量中，不放入前端请求。提交 PR 后删除本实验 ECI，并核对关联 EIP 是否仍独立存在、计费；实验 Key 建议废除。

实例与 EIP 清理结果待完成后记录。
