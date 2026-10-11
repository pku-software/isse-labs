# ============================================================
# 构建阶段：准备运行环境（安装依赖、复制文件）
# ============================================================

# 选择官方 Python 精简镜像作为基础环境；3.11 与 Flask、requests、gunicorn 均兼容
FROM python:3.11-slim

# 让 Python 输出不经过缓冲，容器日志能及时出现在 ECI 控制台；
# 同时不生成 .pyc 文件，保持镜像干净
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 设置容器内的工作目录，后续的相对路径都以它为准
# （app.py 里的 send_from_directory("frontend", ...) 依赖这个位置）
WORKDIR /app

# 先只复制依赖清单：源码改动频繁，依赖清单很少变
COPY requirements.txt ./

# 在构建阶段安装依赖（含 gunicorn）；不保留 pip 缓存以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 再复制应用代码和前端静态文件
COPY app.py ./
COPY frontend/ ./frontend/

# 声明容器预期对外提供的端口（只是元数据，不会自动创建公网入口）
EXPOSE 5001

# ============================================================
# 运行阶段：镜像启动时执行
# ============================================================

# 用 Gunicorn 启动 Flask 应用：单 worker，监听 0.0.0.0:5001，
# 超时设为 120 秒（调用 DeepSeek 可能需要较长时间，默认 30 秒会被误杀）
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "--timeout", "120", "app:app"]
