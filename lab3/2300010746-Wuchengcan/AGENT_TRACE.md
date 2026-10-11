姓名：邬程灿

学号：2300010746



后续如果需要我操作，包括创建云服务器，提供信息，随时跟我说

个人分支和目录已经建好，名称是 lab3/2300010746-Wuchengcan。邬程灿的拼音我写成了 Wuchengcan。如果这个拼写不对，在提交之前告诉我。

Lab 2 里运行应用需要的文件已经复制到这个新目录：app.py、frontend/、requirements.txt、.gitignore、.env.example 和项目说明。没有复制对话轨迹、.env 和虚拟环境，Lab 2 原来的目录也没有改。

当前应用是这样工作的。浏览器打开 / 时，Flask 返回 frontend/index.html，同时提供 style.css 和 app.js。页面里的 JavaScript 用相对路径调用同一服务：打开时读取全部记录，发送时创建，修改和删除走对应接口。创建记录时，后端用 load_dotenv() 和 os.getenv("DEEPSEEK_API_KEY") 读取密钥，再请求 DeepSeek，把模型回复和这条消息放进内存列表。密钥继续只放在后端，因为前端代码会被下载到浏览器里，写在里面就能被看到。

你确认后，我会做这些最小改动，先不安装 Docker，也不上云：

在 requirements.txt 里加上 Gunicorn
写一份完整的 Dockerfile：用带 Python 的基础镜像，先安装依赖，再复制应用和前端；容器启动时由 Gunicorn 单进程监听 0.0.0.0:5001，同时提供页面、静态文件和接口
写 .dockerignore，把 .env、缓存、虚拟环境和对话轨迹排除在构建之外
保留现有聊天功能。容器里不用 Flask 的调试服务器对公网提供服务
需要你登录云控制台、确认费用、填写密钥或在浏览器里验证时，我会单独告诉你。现在还不到那一步。

看过这个计划后，回复「继续」，我就开始写 Dockerfile。

继续

Dockerfile 已经写在个人目录里。聊天页面、接口和增删改查都还在，容器启动后会由 Gunicorn 提供页面、静态文件和 API。这次还没有提交。

构建阶段按说明书准备环境：选定基础镜像、复制文件、安装依赖，这时应用还没有开始接收请求。运行阶段才执行最后的启动命令，容器起来之后才监听端口。改了源码之后，已经建好的镜像不会自己更新，需要重新构建。

实际文件是：

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY frontend ./frontend
EXPOSE 5001
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "app:app"]
FROM python:3.12-slim 选择官方的 Python 3.12 精简镜像作为基础环境。当前依赖能在这个版本上安装，镜像里也不会自带实验密钥。

WORKDIR /app 把容器内的工作目录设为 /app。后面的复制和安装都相对这个目录，Flask 找 frontend/ 时也从这里找。

COPY requirements.txt . 先只复制依赖清单。构建时的上下文是个人目录 lab3/2300010746-Wuchengcan/，不是整个仓库。

RUN pip install --no-cache-dir -r requirements.txt 在构建阶段安装依赖，其中包含新加上的 Gunicorn。这一步失败的话，要看构建日志，后面的步骤不会继续。

COPY app.py . 和 COPY frontend ./frontend 再复制应用和前端。页面、样式、脚本和接口因此都在同一个镜像里。前端仍然用相对路径请求 /api/messages，所以会打到同一个容器。

EXPOSE 5001 只是声明这个容器预期使用 5001 端口。它不会自动打开公网入口。真正听端口的是下面的启动命令；以后 ECI 还要有公网地址，网络规则也要允许访问。

CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "app:app"] 是容器运行时执行的命令。只开一个 worker，监听所有网卡的 5001 端口。app:app 表示 app.py 里的 Flask 对象 app。密钥仍在运行时用 os.getenv("DEEPSEEK_API_KEY") 读取，没有写进 Dockerfile。直接运行 python app.py 时仍会用本机的调试服务器；容器里走的是这条 Gunicorn 命令。

.dockerignore 让构建上下文不要带上 .env、.git、__pycache__/、.venv/ 和 AGENT_TRACE.md。这样密钥、缓存、虚拟环境和对话轨迹不会进镜像。.gitignore 里已经忽略 .env、__pycache__/ 和 .venv/，.env.example 里仍然只有占位符。

构建按这些指令从上到下执行。某一步失败或中断，后面的步骤不会跑，改完原因后要重新构建。再次构建时，前面没有变化的步骤有可能复用缓存；从发生变化的那一步起，后面通常要重做。云端构建不保证从断点接着跑。

请先按自己的理解回答这两题：

为什么把 requirements.txt 的复制和安装放在复制 app.py、前端之前？可以结合平时改源码和改依赖哪一个更频繁，以及构建时缓存怎么起作用来想。
Dockerfile 写了 EXPOSE 5001，浏览器也去访问 5001，但 Gunicorn 实际监听的是 0.0.0.0:5002。网页会遇到什么问题？只改 EXPOSE 能解决吗？

命名空间

请先创建命名空间

仓库名称

0/64 请先创建命名空间

长度为2-64个字符，可使用小写英文字母、数字，可使用分隔符“_”、“-”、“.”（分隔符不能在首位或末位）

仓库类型

公开

私有

摘要

0/100

 

长度最长100个字符

描述信息

 

支持Markdown格式



这些怎么写

先点「创建命名空间」，建好后再回到这个表单。命名空间填：

wuchengcan
如果提示已被占用，改成 wuchengcan2300010746。这是 ACR 自己的命名空间，不是 GitHub 用户名。

回到创建仓库的页面后这样填：

项目	填写
命名空间
刚创建的 wuchengcan
仓库名称
lab3-chat
仓库类型
私有
摘要
Lab 3 chat app，也可以留空
描述信息
留空
下一步「代码源」再选 GitHub：用户名 ChengcanWu，仓库 isse-labs。那一步不要改成课程官方仓库。填完后把你看到的下一页发过来。

lab3-chat

华北2（北京）

私有

自动构建仓库

正常

基本信息

构建

触发器

镜像版本

基本信息

仓库名称

lab3-chat

lab3-chat

复制

仓库地域

华北2（北京）

仓库类型

私有

代码仓库

https://github.com/ChengcanWu/isse-labs

公网地址

crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat

crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat

复制

专有网络

crpi-fom4qze0yaawfevk-vpc.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat

crpi-fom4qze0yaawfevk-vpc.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat

复制

摘要

lab3-chat

操作指南

制品描述

1. 登录阿里云 Container Registry

$ docker login --username=ChengcanWu crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com

用于登录的用户名为阿里云账号全名，密码为开通服务时设置的密码。



您可以在访问凭证页面修改凭证密码。



注意：使用 RAM 用户（子账号）登录镜像仓库时，不支持企业别名带有英文半角句号（.）。



2. 从Registry中拉取镜像

$ docker pull crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat:[镜像版本号]

3. 将镜像推送到Registry

$ docker login --username=ChengcanWu crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com

$ docker tag [ImageId] crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat:[镜像版本号]

$ docker push crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat:[镜像版本号]

请根据实际镜像信息替换示例中的[ImageId]和[镜像版本号]参数。



4. 选择合适的镜像仓库地址

从ECS推送镜像时，可以选择使用镜像仓库内网地址。推送速度将得到提升并且将不会损耗您的公网流量。



如果您使用的机器位于VPC网络，请使用 crpi-fom4qze0yaawfevk-vpc.cn-beijing.personal.cr.aliyuncs.com 作为Registry的域名登录。



5. 示例

使用"docker tag"命令重命名镜像，并将它通过专有网络地址推送至Registry。



$ docker images

REPOSITORY                                                         TAG                 IMAGE ID            CREATED             VIRTUAL SIZE

registry.aliyuncs.com/acs/agent                                    0.7-dfb6816         37bb9c63c8b2        7 days ago          37.89 MB

$ docker tag 37bb9c63c8b2 crpi-fom4qze0yaawfevk-vpc.cn-beijing.personal.cr.aliyuncs.com/acs/agent:0.7-dfb6816

使用 "docker push" 命令将该镜像推送至远程。



$ docker push crpi-fom4qze0yaawfevk-vpc.cn-beijing.personal.cr.aliyuncs.com/acs/agent:0.7-dfb6816



这样是什么意义，是不是我目前github的改动就会同步到这个仓库里面，之后如果我想要把github上面的项目同步部署到阿里云，是不是这样就行

仓库已经建好，并且绑到了你的 Fork：https://github.com/ChengcanWu/isse-labs。地域是华北 2（北京），类型是私有。页面上的公网地址是以后拉取镜像用的，不是现在要执行的命令。

这还不表示 GitHub 上的改动已经同步过去，也不会自动部署到阿里云。ACR 里目前还没有根据你的代码构建出来的镜像。页面下方的 docker login、docker pull、docker push 是给本机 Docker 手动推镜像用的，这次实验不用做。

接下来的关系是：GitHub 放代码，ACR 按你指定的分支把代码构建成镜像并存起来，后面的 ECI 再拉取这个镜像运行。只有构建规则被触发时，ACR 才会去读 GitHub。你现在看到的「自动构建仓库：正常」只说明这个仓库可以用代码源构建，不代表已经构建成功。

请打开左侧 构建：

优先打开 海外机器构建，其他选项保持默认。
点 添加构建规则，然后保存：
分支：lab3/2300010746-Wuchengcan，不要选 main
构建上下文目录：/lab3/2300010746-Wuchengcan/
Dockerfile：上下文已是个人目录时填 Dockerfile；若页面要求相对仓库根目录，填 lab3/2300010746-Wuchengcan/Dockerfile
镜像版本：lab3-b1dc73e
自动构建：关闭
保存规则后，再点 立即构建。
构建页显示成功后，回复「构建成功」。失败就把构建日志发过来，不要附带密码或密钥。


构建成功

镜像已经由阿里云容器镜像服务在云端构建完成，并保存在你的个人镜像仓库里。

请用自己的话回答这两点：

这次实验里，代码在哪里，构建发生在哪里，镜像保存在哪里？
本地改完代码并提交之后，还要做什么，ACR 才会用到这份新代码重新构建？


## 第一点：浏览器里的一次请求，经过哪些环节，才会到达 ECI 里的 Flask？



一次请求从浏览器到 ECI 里的 Flask，大致经过这些环节：



1. **浏览器发起请求**

   在地址栏输入公网地址，浏览器把它解析成一个 HTTP 请求，目标是那个公网 IP 和端口（比如 5001）。



2. **公网 IP / 域名解析**

   如果用的是域名，先经过 DNS 解析成 ECI 实例绑定的公网 IP。这个公网地址是阿里云分配给 ECI 的。



3. **到达阿里云网络边界**

   请求进入阿里云的网络，阿里云根据 ECI 的公网地址和网络规则，把流量路由到对应的 ECI 实例。



4. **ECI 的网络规则 / 安全组**

   ECI 实例上配置的网络规则（安全组、端口放行）决定这个请求是否允许进入。只有规则允许的端口（比如 5001）才会被放行，其他端口会被丢弃。



5. **进入容器**

   请求到达 ECI 里运行的容器。容器是之前从 ACR 拉下来的镜像启动的，里面跑着 Gunicorn。



6. **Gunicorn 监听并转发**

   容器里的 Gunicorn 按 `--bind 0.0.0.0:5001` 监听 5001 端口，收到请求后按 WSGI 协议交给 Flask 应用对象 `app`。



7. **Flask 处理请求**

   Flask 根据路由匹配，找到对应的视图函数，处理业务逻辑，可能读文件、调 API（比如 DeepSeek），然后生成响应。



8. **响应原路返回**

   Flask → Gunicorn → 容器网络 → ECI 网络 → 阿里云网络 → 浏览器。



所以链路是：**浏览器 → DNS/公网 IP → 阿里云网络 → ECI 网络规则 → 容器 → Gunicorn → Flask**。



---



## 第二点：为什么另一台设备也能打开同一个地址？



因为那个公网地址不是绑在某一台设备上的，而是绑在 **ECI 实例**上的。



- ECI 实例有独立的公网 IP，只要它还在运行，这个地址就指向它。

- 任何能访问公网的设备，只要网络规则允许、端口放行，都可以向这个地址发请求。

- 服务端不区分请求来自哪台设备，Flask 收到请求就按逻辑处理，返回同样的页面。



所以另一台设备能打开，不是因为“共享”了什么，而是因为**这个地址是公网可达的，服务本身对所有来访者开放**。谁访问都行，跟设备无关。



---



## 第三点：陌生人如果知道这个公网地址，可能造成什么？



因为地址是公开可达的，陌生人知道后可以：



1. **直接访问页面和接口**

   看到聊天页面，调用 `/api/messages` 等接口，像正常用户一样使用。



2. **消耗资源**

   如果接口背后调用了 DeepSeek API，陌生人可以不断发请求，消耗你的 API 额度、产生费用。



3. **读、改、删数据**

   实验里的增删改查接口没有认证，陌生人可以查看所有消息、发新消息、改或删已有消息，破坏数据。



4. **探测和攻击**

   如果 Flask 或依赖有漏洞，陌生人可以尝试利用；也可能被扫描器发现，成为攻击目标。



5. **滥用作为跳板**

   如果服务有 SSRF 之类的漏洞，可能被用来访问内网或其他服务。



6. **信息泄露**

   如果页面或接口暴露了环境变量、日志、调试信息，可能泄露 API Key 等敏感内容。



所以公网地址不能随便暴露。实验环境里应该：

- 只在需要时开放，用完及时关闭或释放 ECI

- 网络规则只放行必要端口

- 接口加认证

- 不要把密钥写进代码或镜像



一句话：**公网地址等于把服务放在互联网上，谁都能敲，所以要么限制访问，要么用完就关。**

请求路径是对的。这次浏览器直接访问弹性公网 IP 47.94.16.145 的 5001 端口，没有经过域名解析。流量到达该地址后，安全组放行 TCP 5001，容器里的 Gunicorn 再把请求交给 Flask 的 app，响应沿同一条路径回到浏览器。

另一台设备能打开，是因为这个地址属于正在运行的 ECI，不属于你的电脑。任何人只要能访问公网，就能向它发请求。

陌生人知道地址后，可以查看、发送、修改和删除消息；发送消息会调用 DeepSeek 并消耗额度。页面走的是 HTTP，聊天内容在传输中不加密。提交 PR 之后要删除这台实例。

访问方式、实例配置和验证结果已经写进个人 README.md，两张截图也放进了 screenshots/。提交号是 ab3129b。这份说明不用重新构建镜像。

下一步请保存这次的真实对话。在侧边栏的本对话标题上右击，选择「复制」，再选择「复制为 Markdown」，把全文粘贴到 lab3/2300010746-Wuchengcan/AGENT_TRACE.md。如果当前账号能分享这段对话，也可以把真实分享链接写进这个文件。不要把 API Key 或云账号密码写进去。粘贴后告诉我。

我会检查轨迹并提交。然后你把分支推到自己的 Fork，用中文发起 PR。PR 创建之后，再删除实例 eci-2zeenwsi6qz0ux0htsph。实例现在仍在计费。

右击了，点那个

这些都不要点。关掉这个菜单。

「复制为 Markdown」不在对话列表的右键菜单里。请打开这次对话，在聊天窗口顶部右侧找到「...」，选择 Export Chat。它会把整段对话导出成一个 Markdown 文件。

把该文件保存或移动到：

lab3/2300010746-Wuchengcan/AGENT_TRACE.md

保存后告诉我。导出内容里不要包含 API Key 或云账号密码。

这个仍是左侧列表的右键菜单，里面没有导出。不要点 Unpin、Fork Chat 或 Delete。

请左键单击列表里的 Lab 3，让这段对话在右侧打开。然后看右侧对话区域的最上方，标题旁边或右上角有一个 ...。点它，选择 Export Chat。

导出的 Markdown 保存为：

lab3/2300010746-Wuchengcan/AGENT_TRACE.md

如果右侧顶部没有 ...，把你在对话窗口顶部能看到的按钮发我。要导出的是 Lab 3，不是上面的 Lab 2。