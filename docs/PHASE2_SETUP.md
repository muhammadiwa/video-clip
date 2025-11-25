# Phase 2 Setup Guide - Core AI & Processing

## Overview

Phase 2 mengimplementasikan fitur inti AI dan video processing untuk Viral Clip AI:
- ✅ FFmpeg video processing
- ✅ YouTube downloader (yt-dlp)
- ✅ OpenAI Whisper transcription
- ✅ Scene detection
- ✅ Viral moment scoring
- ✅ Celery job queue dengan Redis
- ✅ Progress tracking & notifications

---

## Prerequisites

### 1. Install FFmpeg

**Windows:**
```bash
# Download dari https://ffmpeg.org/download.html
# Atau gunakan Chocolatey:
choco install ffmpeg

# Verify installation
ffmpeg -version
```

**MacOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. Install Redis

**Windows:**
```bash
# Download dari https://github.com/microsoftarchive/redis/releases
# Atau gunakan Docker:
docker run -d -p 6379:6379 redis:latest

# Atau gunakan Memurai (Windows native Redis):
# Download dari https://www.memurai.com/
```

**MacOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Verify Redis:**
```bash
redis-cli ping
# Should return: PONG
```

---

## Installation

### 1. Install Python Dependencies

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**Note:** Installing AI/ML dependencies (PyTorch, Whisper, SceneDetect) might take 10-15 minutes and require ~3GB disk space.

### 2. Download Whisper Model (Optional)

Whisper akan otomatis download model saat pertama kali digunakan. Untuk pre-download:

```python
import whisper
whisper.load_model("base")  # 142MB
# Available models: tiny, base, small, medium, large
```

### 3. Configure Environment

Create `.env` file di folder `backend/`:

```env
# Database
DATABASE_URL=sqlite:///./viralclip.db

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI API Key (optional - hanya untuk GPT-4 features)
OPENAI_API_KEY=your_openai_api_key_here

# AWS S3 (optional - untuk Phase 5)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=your_bucket_name
AWS_REGION=us-east-1

# JWT Secret
SECRET_KEY=your-secret-key-change-in-production

# Directories
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
MAX_UPLOAD_SIZE=2000000000
```

---

## Running the Application

### Terminal 1: Redis Server

```bash
# If not running as service
redis-server
```

### Terminal 2: FastAPI Backend

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: Celery Worker

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Windows:
celery -A app.core.celery_app worker --loglevel=info --pool=solo

# Mac/Linux:
celery -A app.core.celery_app worker --loglevel=info
```

**Note:** Windows memerlukan `--pool=solo` flag karena Celery limitation di Windows.

### Terminal 4: Frontend (optional)

```bash
cd frontend
npm install
npm run dev
```

---

## Testing the Features

### 1. Check API Documentation

Open browser: http://localhost:8000/docs

### 2. Upload Video & Process

```bash
# Upload video
curl -X POST "http://localhost:8000/api/videos/upload" \
  -F "project_id=1" \
  -F "file=@path/to/video.mp4"

# Response:
# {
#   "id": 1,
#   "project_id": 1,
#   "filename": "20231125_120000.mp4",
#   "status": "uploaded",
#   ...
# }

# Trigger processing
curl -X POST "http://localhost:8000/api/processing/process-video" \
  -H "Content-Type: application/json" \
  -d '{"video_id": 1}'

# Response:
# {
#   "job_id": "abc123-def456-...",
#   "status": "started",
#   "message": "Video processing started"
# }

# Check job status
curl "http://localhost:8000/api/jobs/status/{job_id}"
```

### 3. Download from YouTube

```bash
curl -X POST "http://localhost:8000/api/processing/download-youtube" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

### 4. Transcribe Video

```bash
curl -X POST "http://localhost:8000/api/processing/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": 1,
    "language": "en"
  }'
```

### 5. Detect Scenes

```bash
curl -X POST "http://localhost:8000/api/processing/detect-scenes" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": 1,
    "threshold": 27.0
  }'
```

### 6. Detect Viral Moments

```bash
curl -X POST "http://localhost:8000/api/processing/detect-viral" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": 1,
    "top_n": 5
  }'
```

### 7. Full Pipeline

```bash
# Run all processing steps in sequence
curl -X POST "http://localhost:8000/api/processing/process-pipeline" \
  -H "Content-Type: application/json" \
  -d '{"video_id": 1}'
```

---

## API Endpoints

### Video Processing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/processing/process-video` | POST | Extract metadata, thumbnail, audio |
| `/api/processing/download-youtube` | POST | Download from YouTube URL |
| `/api/processing/transcribe` | POST | Transcribe audio to text |
| `/api/processing/detect-scenes` | POST | Detect scene changes |
| `/api/processing/detect-viral` | POST | Detect viral moments |
| `/api/processing/process-pipeline` | POST | Run full AI pipeline |
| `/api/processing/trim-video` | POST | Trim video to time range |
| `/api/processing/compress-video` | POST | Compress video file |

### Job Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jobs/status/{job_id}` | GET | Get job status & progress |
| `/api/jobs/cancel/{job_id}` | POST | Cancel running job |
| `/api/jobs/active` | GET | List active jobs |
| `/api/jobs/scheduled` | GET | List scheduled jobs |
| `/api/jobs/stats` | GET | Get Celery statistics |

---

## Monitoring

### 1. Celery Flower (Web UI)

```bash
# Install Flower
pip install flower

# Start Flower
celery -A app.core.celery_app flower --port=5555
```

Open browser: http://localhost:5555

### 2. Redis CLI

```bash
# Connect to Redis
redis-cli

# Check keys
KEYS *

# Monitor commands
MONITOR

# Get queue length
LLEN celery

# Exit
exit
```

### 3. Check Logs

Celery worker akan menampilkan logs real-time:
- Task received
- Task started
- Task progress
- Task completed/failed

---

## Troubleshooting

### Issue: FFmpeg not found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:**
1. Install FFmpeg (see Prerequisites)
2. Verify: `ffmpeg -version`
3. Add FFmpeg to PATH
4. Restart terminal

### Issue: Redis connection failed

**Error:** `redis.exceptions.ConnectionError: Error 10061 connecting to localhost:6379`

**Solution:**
1. Start Redis server: `redis-server`
2. Or start Redis service (if installed as service)
3. Verify: `redis-cli ping`

### Issue: Celery worker not starting

**Error:** `AttributeError: 'str' object has no attribute 'items'`

**Solution (Windows):**
```bash
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

### Issue: Whisper model download slow

**Solution:**
- Whisper akan download model (~142MB untuk base model) saat pertama kali digunakan
- Download manual: `python -c "import whisper; whisper.load_model('base')"`
- Gunakan model yang lebih kecil: `tiny` (39MB) untuk testing

### Issue: Out of memory (Whisper)

**Solution:**
- Gunakan model yang lebih kecil: `tiny` atau `base`
- Update `app/services/transcription.py`: `DEFAULT_MODEL = "tiny"`

### Issue: PyTorch installation failed

**Solution (Windows):**
```bash
# Install CPU-only version (smaller, faster download)
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu
```

---

## Performance Tips

### 1. Model Selection

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39MB | Very Fast | Basic |
| base | 142MB | Fast | Good |
| small | 466MB | Medium | Better |
| medium | 1.5GB | Slow | Great |
| large | 2.9GB | Very Slow | Best |

**Rekomendasi:**
- Development: `tiny` atau `base`
- Production: `small` atau `medium`

### 2. Celery Concurrency

```bash
# Start multiple workers
celery -A app.core.celery_app worker --concurrency=4 --loglevel=info
```

### 3. Redis Memory

```bash
# Check Redis memory usage
redis-cli INFO memory

# Set max memory (optional)
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Next Steps

**Phase 2 Complete! ✅**

**What's working:**
- ✅ Video upload & processing
- ✅ YouTube downloader
- ✅ FFmpeg video operations
- ✅ Whisper transcription
- ✅ Scene detection
- ✅ Viral moment scoring
- ✅ Background job queue
- ✅ Progress tracking

**What's next (Phase 3):**
- 🔐 Authentication & authorization
- 👤 User management
- 🔑 API key system
- 🚦 Rate limiting
- 📧 Email notifications

**What's next (Phase 4):**
- 🎬 Video editor UI
- ⏱️ Timeline component
- ✂️ Trim/split tools
- 📝 Subtitle editor
- 🎨 Overlay editor

---

## Resources

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [OpenAI Whisper GitHub](https://github.com/openai/whisper)
- [PySceneDetect Docs](https://scenedetect.com/docs/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/documentation)

---

## Support

Jika ada masalah atau pertanyaan:
1. Check error logs di Celery worker
2. Check Redis connection: `redis-cli ping`
3. Verify FFmpeg: `ffmpeg -version`
4. Check API docs: http://localhost:8000/docs
