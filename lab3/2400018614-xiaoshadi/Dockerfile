# 构建一个可以运行 Flask 聊天应用的镜像。
# 构建阶段准备环境和依赖，运行阶段由 Gunicorn 启动应用。

# 选择自带 Python 的官方基础镜像，作为容器的运行环境
FROM python:3.12-slim

# 设置容器内的工作目录，之后的相对路径都相对它解析
WORKDIR /app

# 先只复制依赖清单，让这一步的结果可以被单独缓存
COPY requirements.txt .
# 在构建阶段安装依赖（含 gunicorn）
RUN pip install --no-cache-dir -r requirements.txt

# 再复制应用代码与前端资源
COPY app.py .
COPY frontend ./frontend

# 声明容器预期对外提供的端口（这是元数据，不会自动开通公网）
EXPOSE 5001

# 镜像运行时启动 Gunicorn：单 worker 监听 0.0.0.0:5001，加载 app.py 里的 app 对象
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "--timeout", "90", "app:app"]
