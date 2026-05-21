FROM python:3.11-slim

# Install Node.js
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Copy to backend
RUN cp -r out ../backend/static

# Install Python dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Create data directories
RUN mkdir -p data/cache data/logs

# Expose port
EXPOSE 8000

# Run
CMD ["python", "run.py"]
