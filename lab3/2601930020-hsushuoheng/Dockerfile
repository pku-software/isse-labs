FROM python:3.11-slim

WORKDIR /app

# 先複製依賴清單並安裝，利用 Docker 層級快取機制
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼及前端靜態資源
COPY . .

# 聲明容器服務預期監聽的連接埠
EXPOSE 5001

# 容器啟動時使用 Gunicorn 生產級 WSGI 伺服器
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "app:app"]
