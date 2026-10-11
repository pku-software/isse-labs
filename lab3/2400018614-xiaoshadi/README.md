# Lab 3：AI 聊天应用的容器化与云端部署

本项目由 Lab 2 的 HTML / CSS / JavaScript + Flask + DeepSeek 聊天应用延续而来。Lab 3 不再增加聊天功能，而是把已有应用打包成容器镜像，并放到云端的弹性容器实例（ECI）上运行，让浏览器可以通过公网访问。

## 项目功能

- 浏览器打开聊天页面，输入消息后发送给后端；
- 后端调用 DeepSeek API 生成真实回复；
- 以“一次问答”为一条聊天记录，支持创建、读取、修改、删除；
- API Key 只保存在后端运行时环境变量中，前端不接触、不保存 Key。

## 目录结构

```text
2400018614-xiaoshadi/
├── app.py              # Flask 后端：同时提供前端页面和聊天 API
├── frontend/           # 前端页面与静态资源
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt    # Python 依赖（含 gunicorn）
├── Dockerfile          # 镜像构建说明
├── .dockerignore       # 构建上下文排除项
├── .gitignore          # Git 忽略项（.env、缓存、虚拟环境）
├── .env.example        # 环境变量示例，只有占位值
└── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 API Key

把 `.env.example` 复制为 `.env`，填入自己的 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=your_api_key_here
```

`.env` 已被 `.gitignore` 忽略，不会被提交；真实 Key 不要写入代码或提交到仓库。

## 启动应用

开发时可以直接用 Flask：

```bash
python app.py
```

在容器或正式运行场景中，用 Gunicorn 启动：

```bash
gunicorn --bind 0.0.0.0:5001 --workers 1 --timeout 90 app:app
```

启动后浏览器访问 http://localhost:5001/ 。

## API 清单

| 方法   | 路径                 | 作用                    |
| ------ | -------------------- | ----------------------- |
| GET    | `/api/hello`         | 连通性检查              |
| GET    | `/api/messages`      | 读取全部聊天记录        |
| POST   | `/api/messages`      | 创建记录并调用 DeepSeek |
| PATCH  | `/api/messages/<id>` | 修改指定记录的 message  |
| DELETE | `/api/messages/<id>` | 删除指定记录            |

最简单的接口测试：

```bash
curl http://localhost:5001/api/hello
```

## 容器化

`Dockerfile` 说明镜像如何构建：选择 Python 基础镜像、先安装依赖、再复制应用与前端，最后由 Gunicorn 监听 `0.0.0.0:5001` 启动 Flask 应用。本实验不要求在本机安装 Docker，只用它在云端（ACR）构建。

## 云端构建（ACR）

本节记录本次实验使用的阿里云容器镜像服务（ACR）配置：ACR 从个人 GitHub Fork 的分支在云端构建镜像并保存，ECI 再拉取该镜像运行。

- 地域：华北 2（北京）
- 镜像命名空间：`shadi_10086`
- 镜像仓库：`lab3`
- 构建分支：`lab3/2400018614-xiaoshadi`
- 构建上下文目录：`lab3/2400018614-xiaoshadi`
- Dockerfile 文件名：`Dockerfile`
- 镜像版本（Tag）：`lab3-a2e40bc`
- 镜像地址：`registry.cn-beijing.aliyuncs.com/shadi_10086/lab3:lab3-a2e40bc`

本地代码更新后，需要先提交并 Push 到个人 Fork 的对应分支，再到 ACR 触发一次新的构建，才能得到包含新代码的镜像。

## 云端部署（ECI）

本次实验用阿里云弹性容器实例（ECI）运行上面构建好的镜像，并通过自动创建的弹性公网 IP 提供访问。

- 地域：华北 2（北京）
- 实例名称：`lab3-2400018614`
- 实例规格：经济型，0.25 vCPU / 512 MiB
- 使用镜像：`registry.cn-beijing.aliyuncs.com/shadi_10086/lab3:lab3-a2e40bc`（ECI 从同账号 ACR 拉取）
- 容器端口：Gunicorn 监听 `0.0.0.0:5001`，由 Dockerfile 的 `CMD` 决定
- 安全组：入方向放行 `TCP 5001`，授权对象 `0.0.0.0/0`，否则公网无法访问
- 环境变量：`DEEPSEEK_API_KEY`，值由运行者在 ECI 控制台手动填入，不写入镜像或仓库
- 公网访问地址：`http://123.56.221.65:5001/`

### 验证结果

- 浏览器访问 `http://123.56.221.65:5001/`，页面正常加载；
- `GET /api/hello` 返回 `{"message":"你好"}`；
- `/app.js`、`/style.css` 等静态资源返回 200，没有 404；
- 在页面中发消息能得到 DeepSeek 的真实回复，修改、删除记录均正常。

相关截图见 `screenshots/eci-created.png`（实例创建成功）与 `screenshots/public-page.png`（浏览器实际访问公网页面，含地址栏）。

### 安全与清理

- 公网入口使用 **HTTP**，聊天内容在链路上**不加密**，请勿输入敏感信息；
- 聊天 API **无鉴权**，任何人知道地址都可以调用，会消耗后端 Key 的额度；
- 实验结束后**必须删除该 ECI 实例**，并检查为其自动创建的弹性公网 IP（EIP）是否仍在单独计费；实验用 API Key 建议随后废弃。
