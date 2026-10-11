# 以官方 Python 镜像为基础：里面已经有 Python 3.12、pip 和常用系统库。
# slim 变体体积更小；基础镜像里不含任何实验 Key。
FROM python:3.12-slim

# 设定容器内的工作目录为 /app，后面所有相对路径都以它为准。
WORKDIR /app

# 先只复制依赖清单，让这一层在源码变化时可以复用构建缓存。
COPY requirements.txt ./

# 在构建阶段安装依赖（含 Gunicorn）；
# --no-cache-dir 避免把 pip 的下载缓存留在镜像里。
RUN pip install --no-cache-dir -r requirements.txt

# 再复制应用代码与前端静态文件；
# .dockerignore 会把 .env、虚拟环境、轨迹等排除在构建上下文之外。
COPY app.py ./
COPY frontend ./frontend

# 声明容器计划对外提供 5001 端口；
# 这只是元数据，不会自动创建公网入口。
EXPOSE 5001

# 镜像启动时执行：用 Gunicorn 单 worker 监听 0.0.0.0:5001，
# 入口是 app.py 中的 Flask 对象 app。
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "app:app"]
