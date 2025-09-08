FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./

RUN uv sync --no-cache

COPY . .

CMD uv run uvicorn main:app --host 0.0.0.0 --port $SERVER_PORT
