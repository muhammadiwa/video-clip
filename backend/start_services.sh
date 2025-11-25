#!/bin/bash

echo "============================================"
echo "Viral Clip AI - Starting Services"
echo "============================================"
echo ""

# Check Redis
echo "Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "[ERROR] Redis is not running!"
    echo "Please start Redis server first:"
    echo "  - Run: redis-server"
    echo "  - Or: brew services start redis (Mac)"
    echo "  - Or: sudo systemctl start redis-server (Linux)"
    echo "  - Or: docker run -d -p 6379:6379 redis:latest"
    exit 1
fi
echo "[OK] Redis is running"

# Check FFmpeg
echo ""
echo "Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARNING] FFmpeg not found in PATH"
    echo "Video processing features will not work."
    echo "Please install FFmpeg:"
    echo "  - Mac: brew install ffmpeg"
    echo "  - Linux: sudo apt install ffmpeg"
else
    echo "[OK] FFmpeg is available"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Start services in background
echo ""
echo "============================================"
echo "Starting FastAPI Backend..."
echo "============================================"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo ""
echo "============================================"
echo "Starting Celery Worker..."
echo "============================================"
celery -A app.core.celery_app worker --loglevel=info &
CELERY_PID=$!

echo ""
echo "============================================"
echo "Services Started!"
echo "============================================"
echo ""
echo "FastAPI Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Celery PID: $CELERY_PID"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $CELERY_PID; echo 'Services stopped.'; exit" SIGINT SIGTERM

wait
