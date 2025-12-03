from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import os
import shutil
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import settings
from app.models.video import Video
from app.models.clip import Clip
from app.models.project import Project

router = APIRouter()

class StorageStats(BaseModel):
    total_size_bytes: int
    total_size_formatted: str
    uploads_size: int
    temp_size: int
    exports_size: int
    videos_count: int
    clips_count: int
    projects_count: int

class CleanupResult(BaseModel):
    files_deleted: int
    space_freed_bytes: int
    space_freed_formatted: str
    errors: List[str]

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def get_directory_size(path: str) -> int:
    """Get total size of directory in bytes"""
    total = 0
    if os.path.exists(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
    return total

@router.get("/stats", response_model=StorageStats)
def get_storage_stats(db: Session = Depends(get_db)):
    """Get storage statistics"""
    base_dir = Path(settings.UPLOAD_DIR).parent
    uploads_dir = Path(settings.UPLOAD_DIR)
    temp_dir = Path(settings.TEMP_DIR)
    
    uploads_size = get_directory_size(str(uploads_dir))
    temp_size = get_directory_size(str(temp_dir))
    exports_size = 0
    
    # Calculate exports size from clips
    clips = db.query(Clip).filter(Clip.exported == True).all()
    for clip in clips:
        if clip.export_path and os.path.exists(clip.export_path):
            exports_size += os.path.getsize(clip.export_path)
    
    total_size = uploads_size + temp_size
    
    return StorageStats(
        total_size_bytes=total_size,
        total_size_formatted=format_size(total_size),
        uploads_size=uploads_size,
        temp_size=temp_size,
        exports_size=exports_size,
        videos_count=db.query(Video).count(),
        clips_count=db.query(Clip).count(),
        projects_count=db.query(Project).count()
    )

@router.post("/cleanup-temp", response_model=CleanupResult)
def cleanup_temp_files(max_age_hours: int = 24, db: Session = Depends(get_db)):
    """Clean up temporary files older than specified hours"""
    temp_dir = Path(settings.TEMP_DIR)
    files_deleted = 0
    space_freed = 0
    errors = []
    
    if not temp_dir.exists():
        return CleanupResult(
            files_deleted=0,
            space_freed_bytes=0,
            space_freed_formatted="0 B",
            errors=[]
        )
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    for item in temp_dir.rglob("*"):
        if item.is_file():
            try:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff_time:
                    size = item.stat().st_size
                    item.unlink()
                    files_deleted += 1
                    space_freed += size
            except Exception as e:
                errors.append(f"{item}: {str(e)}")
    
    # Remove empty directories
    for item in sorted(temp_dir.rglob("*"), reverse=True):
        if item.is_dir():
            try:
                item.rmdir()
            except OSError:
                pass  # Directory not empty
    
    return CleanupResult(
        files_deleted=files_deleted,
        space_freed_bytes=space_freed,
        space_freed_formatted=format_size(space_freed),
        errors=errors
    )

@router.post("/cleanup-orphaned", response_model=CleanupResult)
def cleanup_orphaned_files(db: Session = Depends(get_db)):
    """Clean up files not associated with any database record"""
    uploads_dir = Path(settings.UPLOAD_DIR)
    files_deleted = 0
    space_freed = 0
    errors = []
    
    # Get all valid file paths from database
    valid_paths = set()
    
    videos = db.query(Video).all()
    for video in videos:
        if video.file_path:
            valid_paths.add(os.path.abspath(video.file_path))
        if video.audio_path:
            valid_paths.add(os.path.abspath(video.audio_path))
        if video.thumbnail_path:
            valid_paths.add(os.path.abspath(video.thumbnail_path))
        if video.transcription_path:
            valid_paths.add(os.path.abspath(video.transcription_path))
        if video.scenes_path:
            valid_paths.add(os.path.abspath(video.scenes_path))
    
    clips = db.query(Clip).all()
    for clip in clips:
        if clip.export_path:
            valid_paths.add(os.path.abspath(clip.export_path))
    
    # Scan uploads directory for orphaned files
    if uploads_dir.exists():
        for item in uploads_dir.rglob("*"):
            if item.is_file():
                abs_path = os.path.abspath(str(item))
                if abs_path not in valid_paths:
                    try:
                        size = item.stat().st_size
                        item.unlink()
                        files_deleted += 1
                        space_freed += size
                    except Exception as e:
                        errors.append(f"{item}: {str(e)}")
    
    return CleanupResult(
        files_deleted=files_deleted,
        space_freed_bytes=space_freed,
        space_freed_formatted=format_size(space_freed),
        errors=errors
    )

@router.delete("/project/{project_id}/cleanup", response_model=CleanupResult)
def cleanup_project_files(project_id: int, db: Session = Depends(get_db)):
    """Delete all files for a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files_deleted = 0
    space_freed = 0
    errors = []
    
    # Delete project directory
    project_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    if project_dir.exists():
        try:
            for item in project_dir.rglob("*"):
                if item.is_file():
                    space_freed += item.stat().st_size
                    files_deleted += 1
            shutil.rmtree(str(project_dir))
        except Exception as e:
            errors.append(f"Failed to delete project directory: {str(e)}")
    
    # Delete temp files for project
    temp_project_dir = Path(settings.TEMP_DIR) / str(project_id)
    if temp_project_dir.exists():
        try:
            for item in temp_project_dir.rglob("*"):
                if item.is_file():
                    space_freed += item.stat().st_size
                    files_deleted += 1
            shutil.rmtree(str(temp_project_dir))
        except Exception as e:
            errors.append(f"Failed to delete temp directory: {str(e)}")
    
    return CleanupResult(
        files_deleted=files_deleted,
        space_freed_bytes=space_freed,
        space_freed_formatted=format_size(space_freed),
        errors=errors
    )

@router.get("/project/{project_id}/size")
def get_project_storage(project_id: int, db: Session = Depends(get_db)):
    """Get storage used by a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    temp_dir = Path(settings.TEMP_DIR) / str(project_id)
    
    uploads_size = get_directory_size(str(project_dir))
    temp_size = get_directory_size(str(temp_dir))
    total_size = uploads_size + temp_size
    
    videos_count = db.query(Video).filter(Video.project_id == project_id).count()
    clips_count = db.query(Clip).filter(Clip.project_id == project_id).count()
    
    return {
        "project_id": project_id,
        "total_size_bytes": total_size,
        "total_size_formatted": format_size(total_size),
        "uploads_size": uploads_size,
        "temp_size": temp_size,
        "videos_count": videos_count,
        "clips_count": clips_count
    }
