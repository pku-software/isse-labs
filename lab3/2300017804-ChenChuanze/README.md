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

本地检查使用 macOS/Python 3.13，不等同于 Linux/Python 3.12 镜像构建验证；未调用真实模型。ACR 构建结果见下文，学生浏览器验证结果待实际完成后补充。

## ACR 云端构建

代码源为个人 Fork `GG-booond/isse-labs`，分支为 `lab3/2300017804-ChenChuanze`，构建上下文为 `/lab3/2300017804-ChenChuanze/`，Dockerfile 位于该上下文中的 `Dockerfile`。

- 地域：华北 2（北京），`cn-beijing`；个人版私有镜像仓库。
- ACR 命名空间：`lab3-2300017804`；镜像仓库：`chat-app`。
- 构建规则：Branch，分支及上下文同上；Dockerfile 文件名为 `Dockerfile`。
- 海外机器构建开启，自动构建关闭，其他选项保持默认。
- 镜像标签：`lab3-89a96ec`，对应代码提交 `89a96ec7d09904097270d72125e26da9eff7bd49`。
- 2026-10-09：Agent 核对 GitHub 远端分支与代码提交一致；学生按上述设置操作 ACR，并报告控制台显示构建成功。
- 具体镜像地址待 ECI 选择镜像时记录。

代码须先 Commit、Push，再触发 ACR 构建；ACR 无法读取仅保留在本机的新提交。本次后续 README 文档更新不需要重新构建镜像。

## ECI 配置与访问验证

ECI 与 ACR 使用同一地域；沿用镜像中的启动命令，应用实际端口为 `5001`，环境变量名称为 `DEEPSEEK_API_KEY`。

实际规格、镜像地址及标签、公网地址、ECI 创建状态和学生浏览器验证结果：待部署后记录。

必交截图在学生完成后保存为 `screenshots/eci-created.<真实扩展名>` 与 `screenshots/public-page.<真实扩展名>`。实验末尾由学生保存真实对话至 `AGENT_TRACE.md`。

本实验短时使用公网 HTTP，浏览器与 ECI 之间的聊天内容不加密，不输入敏感信息。Key 留在后端，不随前端请求传输；聊天 API 没有鉴权，知道公网地址的人可能调用模型并消耗实验额度。ECI 即使无人访问也可能持续计费，创建前由学生核对控制台展示的 ECI 和 EIP 实际价格。

## 资源清理

PR 提交后由学生删除本实验 ECI，并核对关联 EIP 是否需要独立释放；建议随后废除实验 Key。清理状态待实际核验，不以停止访问作为释放依据。
