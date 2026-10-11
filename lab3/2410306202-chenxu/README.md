# Lab 3：从代码到云端 —— ACR 构建与 ECI 部署

本目录是 Lab 3 的个人实验目录（陈旭，学号 2410306202）。

## 一、项目来源与架构

- 课程仓库：ISSE Labs 2026（Fork 自课程官方仓库 `pku-software/isse-labs`）
- 个人 Fork：<https://github.com/LinyuanChen05/isse-labs>
- 本次分支：`lab3/2410306202-chenxu`
- 应用来源：Lab 2 的 `lab2/陈旭-2410306202/`，这里只保留运行所需的非敏感文件

应用仍然是一个 Flask 聊天程序，一个进程同时承担两件事：

1. 提供前端页面与静态资源：`/`、`/style.css`、`/app.js`；
2. 提供聊天 API：会话接口 `/api/conversations...`，另有兼容接口 `/api/messages...`。

前端使用**同源相对路径**的 `fetch()`，不写死后端地址，因此部署到云端后前端无需修改。

**API Key 只由后端持有**：服务端在运行时从环境变量 `DEEPSEEK_API_KEY` 读取 Key，用于调用 DeepSeek。
前端不输入、不接收、不保存 Key。真实 Key 不进入源码、Dockerfile、构建上下文、镜像、日志或对话。

## 二、目录结构

```
lab3/2410306202-chenxu/
├── app.py              # Flask 后端：页面/静态资源 + 聊天 API
├── frontend/           # 前端：index.html、style.css、app.js
├── requirements.txt    # Python 依赖（含 gunicorn）
├── Dockerfile          # 镜像构建说明
├── .dockerignore       # 构建上下文排除项
├── .gitignore          # 忽略 .env、虚拟环境、运行时数据等
├── .env.example        # 只有变量名与占位值
├── README.md
├── screenshots/        # 必交截图（ECI 创建成功、浏览器公网访问）
└── AGENT_TRACE.md      # 真实 Codex 对话轨迹（由学生本人保存）
```

## 三、Dockerfile 关键配置

| 指令 | 作用 |
| --- | --- |
| `FROM python:3.12-slim` | 选择含 Python 的精简基础镜像 |
| `WORKDIR /app` | 设置容器内工作目录 |
| `COPY requirements.txt ./` | 先只复制依赖清单，便于利用构建缓存 |
| `RUN pip install --no-cache-dir -r requirements.txt` | 构建阶段安装依赖（含 gunicorn） |
| `COPY . .` | 复制应用与前端（`.dockerignore` 已排除敏感/无关文件） |
| `EXPOSE 5001` | 声明容器预期提供的端口（元数据，不会自动开放公网） |
| `CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5001", "app:app"]` | 运行阶段以单 worker 的 Gunicorn 启动 Flask 应用，监听 0.0.0.0:5001 |

`.dockerignore` 排除 `.env`、`.git`、`data/`、虚拟环境、`AGENT_TRACE.md`、`screenshots/` 等，
确保真实 Key 与聊天数据不会进入构建上下文和镜像。

## 四、镜像构建（ACR）

- 地域：**华北 2（北京）**
- ACR 个人版镜像命名空间：`chenxulab3`
- 镜像仓库：`isse-labs`（私有）
- 代码源：GitHub，`LinyuanChen05/isse-labs`（个人 Fork）
- 构建分支：`lab3/2410306202-chenxu`（本次提交 `bf2d4a4`）
- 构建上下文目录：`/lab3/2410306202-chenxu/`
- Dockerfile 路径：`Dockerfile`
- 镜像版本标签：`lab3-bf2d4a4`
- 自动构建：关闭；开启"海外机器构建"，手动点击"立即构建"
- 构建结果：成功

镜像地址形如：`registry.cn-beijing.aliyuncs.com/chenxulab3/isse-labs:lab3-bf2d4a4`

**更新代码后的重建流程**：先在本地 Commit 并 Push 到个人 Fork 的同一分支（ACR 只构建已 Push 的代码），
再回到 ACR 该仓库的"构建"页重新触发"立即构建"，才会产生包含新代码的新镜像标签。
只改文档（如本 README）不需要重新构建镜像。

## 五、云端运行（ECI）

- 实例名称：`lab3-2410306202`
- 实例 ID：`eci-2zebku0984o0x50pk4ky`
- 地域 / 可用区：华北 2（北京）/ 北京可用区 H
- 规格：经济型（economy），0.25 vCPU / 512 MiB
- 镜像：`registry.cn-beijing.aliyuncs.com/chenxulab3/isse-labs:lab3-bf2d4a4`
- 启动命令：留空，沿用 Dockerfile 的 `CMD`（Gunicorn 单 worker 监听 `0.0.0.0:5001`）
- 容器环境变量：仅 `DEEPSEEK_API_KEY`（**值不记录在仓库中**，由学生在控制台手动填入）
- 网络：自动创建弹性公网 IP `101.200.190.56`；私网 IP `172.23.105.165`
- 安全组：`sg-2zec7l22epyuu9o0yjxh`（使用页面默认安全组）；虚拟交换机：`vsw-2zedrjn60fltm40iw5kkt`
- 创建时间：2026-10-07 21:50:01
- 访问地址：<http://101.200.190.56:5001/>

创建完成后由 Agent 从公网复核：`/` 返回 200 且为聊天页面 HTML，`/app.js`、`/style.css` 均 200，
`/api/hello` 返回 `{"message":"你好"}`，`/api/conversations` 返回 `[]`（说明镜像中不含任何聊天数据）。

## 六、公网访问与安全说明

- 实际访问方式：学生本人在浏览器打开 <http://101.200.190.56:5001/>，页面、样式与脚本正常加载；
  以非敏感内容提问一次并收到模型回复。原始截图见 `screenshots/public-page.png`（含地址栏公网 IP 与端口）。
- ECI 创建成功的原始截图见 `screenshots/eci-created.png`（实例 `lab3-2410306202`，状态"运行中"）。
- 可以换用另一台设备（如手机）访问同一地址，说明应用已不再局限于本机。

**验证结论**：代码经 GitHub → ACR 云端构建成镜像 → ECI 拉取并运行，公网 HTTP 入口可用，
浏览器可完成页面加载、静态资源加载与一次完整的模型问答。

**风险与边界**：

1. 本实验使用 **HTTP**，浏览器与 ECI 之间的聊天内容**未加密**，浏览器会提示"不安全"，不要输入敏感信息。
2. 聊天 API **没有鉴权**：任何知道该公网地址的人都可以调用，会消耗实验用的 DeepSeek 额度。
3. **API Key 始终只存在于后端**：由 ECI 容器运行时环境变量 `DEEPSEEK_API_KEY` 提供，
   不进入源码、Dockerfile、构建上下文、镜像、前端请求或本 README。
4. 本实验为短时教学演示，**PR 提交后必须删除 ECI 实例**，并检查是否有独立计费的弹性公网 IP。