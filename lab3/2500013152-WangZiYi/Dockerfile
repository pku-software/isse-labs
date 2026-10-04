FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY frontend/ ./frontend/

EXPOSE 5001

CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "--timeout", "120", "app:app"]
