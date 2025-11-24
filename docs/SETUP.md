# Setup Guide - Viral Clip AI

## Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg (for video processing)
- PostgreSQL (optional, SQLite by default)
- Redis (optional, for job queue)

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment variables
```bash
copy .env.example .env
```

Edit `.env` file with your configurations:
- Database URL (default: SQLite)
- OpenAI API key (optional for Phase 1)
- AWS credentials (optional)

### 6. Initialize database
```bash
python init_db.py
```

### 7. Run backend server
```bash
uvicorn main:app --reload
```

Backend will run at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment
```bash
copy .env.example .env.local
```

### 4. Run development server
```bash
npm run dev
```

Frontend will run at: `http://localhost:3000`

## Testing the Application

### 1. Open browser
Navigate to `http://localhost:3000`

### 2. Create a new project
- Click "Get Started Free" or "New Project"
- Fill in project details
- Click "Create Project"

### 3. Upload a video (Phase 1)
- Select the project
- Upload a video file
- View the uploaded video

## Troubleshooting

### Backend Issues

**Issue: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Issue: Database connection error**
- Check `.env` DATABASE_URL
- Ensure database is running (if using PostgreSQL)
- Run `python init_db.py` to recreate tables

**Issue: File upload fails**
- Check `uploads` and `temp` directories exist
- Check file size limit in settings

### Frontend Issues

**Issue: Cannot connect to API**
- Ensure backend is running on `http://localhost:8000`
- Check `.env.local` NEXT_PUBLIC_API_URL

**Issue: Module not found**
```bash
npm install
```

**Issue: Port already in use**
```bash
npm run dev -- -p 3001
```

## Next Steps

After successful setup:
1. Verify backend API at `/docs`
2. Test project creation
3. Test video upload
4. Check database records

## Development Workflow

### Backend Development
1. Make changes to Python files
2. Server auto-reloads (with `--reload` flag)
3. Test endpoints at `/docs`

### Frontend Development
1. Make changes to TypeScript/React files
2. Hot reload automatically
3. View changes in browser

## Production Deployment

See `docs/DEPLOYMENT.md` for production setup guide.
