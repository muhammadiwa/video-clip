from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models.subtitle import Subtitle

router = APIRouter()

class SubtitleCreate(BaseModel):
    clip_id: int
    text: str
    start_time: float
    end_time: float
    language: str = "en"
    style: Optional[dict] = None

class SubtitleUpdate(BaseModel):
    text: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    style: Optional[dict] = None

class SubtitleResponse(BaseModel):
    id: int
    clip_id: int
    text: str
    start_time: float
    end_time: float
    language: str
    style: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.post("/", response_model=SubtitleResponse)
def create_subtitle(subtitle: SubtitleCreate, db: Session = Depends(get_db)):
    db_subtitle = Subtitle(
        clip_id=subtitle.clip_id,
        text=subtitle.text,
        start_time=subtitle.start_time,
        end_time=subtitle.end_time,
        language=subtitle.language,
        style=subtitle.style
    )
    db.add(db_subtitle)
    db.commit()
    db.refresh(db_subtitle)
    return db_subtitle

@router.get("/clip/{clip_id}", response_model=List[SubtitleResponse])
def get_clip_subtitles(clip_id: int, db: Session = Depends(get_db)):
    subtitles = db.query(Subtitle).filter(Subtitle.clip_id == clip_id).all()
    return subtitles

@router.put("/{subtitle_id}", response_model=SubtitleResponse)
def update_subtitle(subtitle_id: int, subtitle_update: SubtitleUpdate, db: Session = Depends(get_db)):
    subtitle = db.query(Subtitle).filter(Subtitle.id == subtitle_id).first()
    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    
    for key, value in subtitle_update.model_dump(exclude_unset=True).items():
        setattr(subtitle, key, value)
    
    db.commit()
    db.refresh(subtitle)
    return subtitle

@router.delete("/{subtitle_id}")
def delete_subtitle(subtitle_id: int, db: Session = Depends(get_db)):
    subtitle = db.query(Subtitle).filter(Subtitle.id == subtitle_id).first()
    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    db.delete(subtitle)
    db.commit()
    return {"message": "Subtitle deleted successfully"}
