from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import shutil
import os
from pathlib import Path
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.video import Video
from app.models.project import Project

router = APIRouter()

class BatchUploadResponse(BaseModel):
    uploaded: List[int]
    failed: List[str]
    message: str

class VideoResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    status: str
    source_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    filename = f"{timestamp}{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create video record
    db_video = Video(
        project_id=project_id,
        filename=filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        source_type="upload",
        status="uploaded"
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    
    # Update project status
    project.status = "processing"
    db.commit()
    
    return db_video

@router.get("/project/{project_id}", response_model=List[VideoResponse])
def get_project_videos(project_id: int, db: Session = Depends(get_db)):
    videos = db.query(Video).filter(Video.project_id == project_id).all()
    return videos

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.delete("/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Delete file
    if os.path.exists(video.file_path):
        os.remove(video.file_path)
    
    db.delete(video)
    db.commit()
    return {"message": "Video deleted successfully"}


@router.post("/batch-upload", response_model=BatchUploadResponse)
async def batch_upload_videos(
    project_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple video files at once"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_ids = []
    failed_files = []
    
    for file in files:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_extension = Path(file.filename).suffix
            filename = f"{timestamp}{file_extension}"
            file_path = upload_dir / filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(file_path)
            
            db_video = Video(
                project_id=project_id,
                filename=filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                source_type="upload",
                status="uploaded"
            )
            db.add(db_video)
            db.commit()
            db.refresh(db_video)
            uploaded_ids.append(db_video.id)
        except Exception as e:
            failed_files.append(f"{file.filename}: {str(e)}")
    
    if uploaded_ids:
        project.status = "processing"
        db.commit()
    
    return BatchUploadResponse(
        uploaded=uploaded_ids,
        failed=failed_files,
        message=f"Uploaded {len(uploaded_ids)} videos, {len(failed_files)} failed"
    )
