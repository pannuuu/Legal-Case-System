# Stage 1: Build React + Vite frontend bundle
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python 3.11 FastAPI + ML + Retrieval runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface \
    NLTK_DATA=/app/.cache/nltk_data \
    PORT=7860

WORKDIR /app

# Create non-root user (UID 1000 matches Hugging Face Spaces default)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/.cache/huggingface /app/.cache/nltk_data /app/backend

COPY backend/requirements.txt /app/backend/requirements.txt

# Install CPU-only PyTorch first to avoid ~2GB CUDA wheels, then backend requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Pre-download NLTK corpora and SentenceTransformer embedding weights into image cache
RUN python -c "import nltk; [nltk.download(p, download_dir='/app/.cache/nltk_data', quiet=True) for p in ('stopwords','wordnet','omw-1.4','punkt','punkt_tab')]" && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')"

# Copy backend code, model artifacts, and persistent retrieval index (.dockerignore excludes .env)
COPY backend/app /app/backend/app
COPY backend/data/models/random_forest_exp3 /app/backend/data/models/random_forest_exp3
COPY backend/data/retrieval_index /app/backend/data/retrieval_index
COPY --from=frontend-builder /app/frontend/dist /app/frontend_dist

RUN chown -R appuser:appuser /app

USER appuser
WORKDIR /app/backend

EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
