FROM node:20-bookworm-slim AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

# Install Python dependencies first for better layer caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code only
COPY backend/app ./app
COPY backend/run.py ./run.py

# Copy built frontend static assets from builder stage
COPY --from=frontend-builder /build/frontend/out ./static

# Create runtime data directories
RUN mkdir -p data/cache data/logs

EXPOSE 8000

CMD ["python", "run.py"]
