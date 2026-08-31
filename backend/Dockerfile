# Stage 1: Builder
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to isolate installed packages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 1. Install CPU-only PyTorch explicitly to avoid multi-gigabyte CUDA bloat
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 2. Install the rest of your requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the FastEmbed model into /opt/fastembed_cache during build
ENV FASTEMBED_CACHE_PATH="/opt/fastembed_cache"
RUN python -c "import os; from fastembed import TextEmbedding; os.makedirs('/opt/fastembed_cache', exist_ok=True); TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/opt/fastembed_cache')"

# Stage 2: Production Runtime
FROM python:3.11-slim

WORKDIR /app

# 3. Copy compiled virtual environment and pre-downloaded model cache
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/fastembed_cache /opt/fastembed_cache
ENV PATH="/opt/venv/bin:$PATH"
ENV FASTEMBED_CACHE_PATH="/opt/fastembed_cache"

# Copy your application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]