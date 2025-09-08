# 1. Builder stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency file(s) first for better caching
COPY pyproject.toml ./

# Install project + dependencies into the system environment
RUN uv pip install . --system --no-cache

# 2. Runtime stage
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local /usr/local

# Copy app source
COPY . .

# Expose Uvicorn's default port
EXPOSE 8000

# Run app
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
