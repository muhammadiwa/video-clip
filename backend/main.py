from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import projects, videos, clips, subtitles

app = FastAPI(
    title="Viral Clip AI API",
    description="AI-powered video editing platform API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(clips.router, prefix="/api/clips", tags=["clips"])
app.include_router(subtitles.router, prefix="/api/subtitles", tags=["subtitles"])

@app.get("/")
def read_root():
    return {
        "name": "Viral Clip AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
