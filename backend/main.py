from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from app.core.config import settings
from app.api import projects, videos, clips, subtitles, jobs, processing, templates, storage, analytics, webhooks, platforms

app = FastAPI(
    title="Viral Clip AI API",
    description="AI-powered video editing platform API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get base directory
BASE_DIR = Path(__file__).resolve().parent

# Ensure uploads directory exists
uploads_dir = BASE_DIR / "uploads"
uploads_dir.mkdir(exist_ok=True)

# Static files
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Routers
from app.api import jobs

app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(clips.router, prefix="/api/clips", tags=["clips"])
app.include_router(subtitles.router, prefix="/api/subtitles", tags=["subtitles"])
app.include_router(processing.router, prefix="/api/processing", tags=["processing"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(storage.router, prefix="/api/storage", tags=["storage"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(webhooks.router)
app.include_router(platforms.router)


@app.get("/")
def read_root():
    return {"name": "Viral Clip AI API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
