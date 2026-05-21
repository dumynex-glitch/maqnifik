#!/bin/bash
set -e

echo "🔨 Building Magnific API Integration App..."
echo ""

# Build frontend
echo "📦 Building Next.js frontend..."
cd frontend
npm install
npm run build

# Copy to backend/static
echo "📋 Copying static files to backend..."
cd ..
rm -rf backend/static
cp -r frontend/out backend/static

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo ""
echo "✅ Build complete!"
echo ""
echo "To run the app:"
echo "  cd backend"
echo "  python run.py"
echo ""
echo "Then open: http://localhost:8000"
