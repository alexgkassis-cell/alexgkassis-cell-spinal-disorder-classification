# Stage 7: production FastAPI inference service (CPU-only TensorFlow)
# The private C08 checkpoint is NOT copied into this Docker image.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY api/ ./api/
RUN pip install --no-cache-dir . \
    && pip install --no-cache-dir -r api/requirements.txt \
    && pip install --no-cache-dir tensorflow-cpu==2.21.0
EXPOSE 8000
# Railway injects the PORT environment variable; one worker avoids model
# duplication in memory and uses the application's inference lock.
CMD ["sh", "-c", "exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
