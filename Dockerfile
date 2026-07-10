# =============================================================================
# LinguaChat — AI Language Learning Buddy
# Production-ready Dockerfile (multi-stage)
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Create non-root user for security
RUN groupadd -r lingua && useradd -r -g lingua -m -d /app lingua

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=lingua:lingua . .

# Health check — Streamlit exposes a health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

USER lingua

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py"]
