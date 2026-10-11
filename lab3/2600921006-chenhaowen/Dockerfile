FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /usr/local/bin/uv
WORKDIR /app
COPY requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt
COPY app.py ./
COPY frontend/ ./frontend/
EXPOSE 5001
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "--timeout", "90", "app:app"]
