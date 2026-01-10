# ============================================
# UMIS (Universal Market Intelligence System)
# Multi-stage Docker Build
# ============================================

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.13-slim AS builder

WORKDIR /build

# System dependencies for native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Selenium/Chrome for DART crawler
    chromium \
    chromium-driver \
    # General utilities
    curl \
    && rm -rf /var/lib/apt/lists/* \
    # Create non-root user
    && useradd -m -s /bin/bash umis

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Copy UMIS source code
COPY --chown=umis:umis umis_rag/ ./umis_rag/
COPY --chown=umis:umis scripts/ ./scripts/
COPY --chown=umis:umis config/ ./config/
COPY --chown=umis:umis data/raw/ ./data/raw/
COPY --chown=umis:umis umis.yaml umis_core.yaml umis_examples.yaml ./
COPY --chown=umis:umis requirements.txt VERSION.txt ./

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/chunks /app/logs \
    && chown -R umis:umis /app/data /app/logs

# Copy entrypoint and healthcheck
COPY --chown=umis:umis docker/entrypoint.sh /entrypoint.sh
COPY --chown=umis:umis docker/healthcheck.py /healthcheck.py
RUN chmod +x /entrypoint.sh

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    CHROMA_PERSIST_DIR=/app/data/chroma \
    LLM_MODE=cursor \
    AUTO_BUILD_RAG=true \
    # Chrome settings for Selenium
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python /healthcheck.py || exit 1

# Run as non-root user
USER umis

ENTRYPOINT ["/entrypoint.sh"]

# Default command: keep container running for exec
CMD ["tail", "-f", "/dev/null"]
