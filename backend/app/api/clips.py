from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models.clip import Clip
from app.models.video import Video

router = APIRouter()

class ClipCreate(BaseModel):
    video_id: int  # Required - clip must belong to a video
    name: str
    description: Optional[str] = None
    start_time: float
    end_time: float
    viral_score: float = 0.0
    category: Optional[str] = None

class ClipUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    aspect_ratio: Optional[str] = None
    resolution: Optional[str] = None
    subtitle_style: Optional[dict] = None
    overlays: Optional[dict] = None

class ClipResponse(BaseModel):
    id: int
    project_id: int
    video_id: int  # Required - clip must belong to a video
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: float
    end_time: float
    duration: float
    viral_score: float
    category: Optional[str] = None
    aspect_ratio: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ClipResponse)
def create_clip(clip: ClipCreate, db: Session = Depends(get_db)):
    # Get video to retrieve project_id
    video = db.query(Video).filter(Video.id == clip.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    duration = clip.end_time - clip.start_time
    db_clip = Clip(
        video_id=clip.video_id,
        project_id=video.project_id,  # Auto-populate from video
        name=clip.name,
        description=clip.description,
        start_time=clip.start_time,
        end_time=clip.end_time,
        duration=duration,
        viral_score=clip.viral_score,
        category=clip.category,
        status="detected"
    )
    db.add(db_clip)
    db.commit()
    db.refresh(db_clip)
    return db_clip

@router.get("/project/{project_id}", response_model=List[ClipResponse])
def get_project_clips(project_id: int, db: Session = Depends(get_db)):
    """Get all clips for a project"""
    clips = db.query(Clip).filter(Clip.project_id == project_id).all()
    return clips

@router.get("/video/{video_id}", response_model=List[ClipResponse])
def get_video_clips(video_id: int, db: Session = Depends(get_db)):
    """Get all clips generated from a specific video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    clips = db.query(Clip).filter(Clip.video_id == video_id).order_by(Clip.viral_score.desc()).all()
    return clips

@router.get("/{clip_id}", response_model=ClipResponse)
def get_clip(clip_id: int, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return clip

@router.put("/{clip_id}", response_model=ClipResponse)
def update_clip(clip_id: int, clip_update: ClipUpdate, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    for key, value in clip_update.model_dump(exclude_unset=True).items():
        setattr(clip, key, value)
    
    # Recalculate duration if times changed
    if clip_update.start_time or clip_update.end_time:
        clip.duration = clip.end_time - clip.start_time
    
    db.commit()
    db.refresh(clip)
    return clip

@router.delete("/{clip_id}")
def delete_clip(clip_id: int, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    db.delete(clip)
    db.commit()
    return {"message": "Clip deleted successfully"}
