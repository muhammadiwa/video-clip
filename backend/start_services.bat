@echo off
echo ============================================
echo Viral Clip AI - Starting Services
echo ============================================
echo.

echo Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Redis is not running!
    echo Please start Redis server first:
    echo   - Run redis-server
    echo   - Or start Redis as a service
    echo   - Or run: docker run -d -p 6379:6379 redis:latest
    pause
    exit /b 1
)
echo [OK] Redis is running

echo.
echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found in PATH
    echo Video processing features will not work.
    echo Please install FFmpeg: https://ffmpeg.org/download.html
)
echo [OK] FFmpeg is available

echo.
echo ============================================
echo Starting FastAPI Backend...
echo ============================================
start cmd /k "title FastAPI Backend && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

echo.
echo ============================================
echo Starting Celery Worker...
echo ============================================
start cmd /k "title Celery Worker && venv\Scripts\activate && celery -A app.core.celery_app worker --loglevel=info --pool=solo"

echo.
echo ============================================
echo Services Started!
echo ============================================
echo.
echo FastAPI Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping services...
taskkill /FI "WindowTitle eq FastAPI Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Celery Worker*" /T /F >nul 2>&1

echo Services stopped.
pause
