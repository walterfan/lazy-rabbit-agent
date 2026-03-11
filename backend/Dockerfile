# ============================================================================
# Lazy Rabbit Agent — Backend
# Multi-stage build: install deps → production image
# ============================================================================

# ---------- Stage 1: Build ----------
FROM python:3.13-slim AS builder

WORKDIR /build

# Install system deps for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==2.1.1

# Copy dependency files first (cache layer)
COPY pyproject.toml poetry.lock ./

# Export requirements (no dev deps)
RUN poetry export -f requirements.txt --without dev --output requirements.txt

# Install Python deps into a virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Stage 2: Production ----------
FROM python:3.13-slim AS production

WORKDIR /app

# Install runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual env from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/chroma data/uploads logs

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser \
    && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run with uvicorn (production: no reload, workers based on CPU)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--access-log"]
