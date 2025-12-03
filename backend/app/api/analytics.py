from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.video import Video
from app.models.clip import Clip
from app.models.project import Project

router = APIRouter()

class OverviewStats(BaseModel):
    total_projects: int
    total_videos: int
    total_clips: int
    total_exported: int
    total_duration_hours: float
    avg_viral_score: float
    processing_success_rate: float

class DailyStats(BaseModel):
    date: str
    videos_processed: int
    clips_generated: int
    clips_exported: int

class TopClip(BaseModel):
    id: int
    title: Optional[str]
    viral_score: float
    duration: float
    video_id: int
    project_id: int
    exported: bool
    created_at: datetime

class PlatformStats(BaseModel):
    platform: str
    count: int
    avg_duration: float

class ViralScoreDistribution(BaseModel):
    range: str
    count: int

@router.get("/overview", response_model=OverviewStats)
def get_overview_stats(db: Session = Depends(get_db)):
    """Get overall platform statistics"""
    total_projects = db.query(Project).count()
    total_videos = db.query(Video).count()
    total_clips = db.query(Clip).count()
    total_exported = db.query(Clip).filter(Clip.exported == True).count()
    
    # Total duration in hours
    total_duration_seconds = db.query(func.sum(Video.duration)).scalar() or 0
    total_duration_hours = total_duration_seconds / 3600
    
    # Average viral score
    avg_viral = db.query(func.avg(Clip.viral_score)).scalar() or 0
    
    # Processing success rate
    processed_videos = db.query(Video).filter(Video.status == 'processed').count()
    error_videos = db.query(Video).filter(Video.status == 'error').count()
    total_attempted = processed_videos + error_videos
    success_rate = (processed_videos / total_attempted * 100) if total_attempted > 0 else 100
    
    return OverviewStats(
        total_projects=total_projects,
        total_videos=total_videos,
        total_clips=total_clips,
        total_exported=total_exported,
        total_duration_hours=round(total_duration_hours, 2),
        avg_viral_score=round(avg_viral, 2),
        processing_success_rate=round(success_rate, 1)
    )

@router.get("/daily", response_model=List[DailyStats])
def get_daily_stats(days: int = 7, db: Session = Depends(get_db)):
    """Get daily processing statistics"""
    results = []
    today = datetime.now().date()
    
    for i in range(days):
        date = today - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        videos_processed = db.query(Video).filter(
            Video.created_at >= start,
            Video.created_at <= end
        ).count()
        
        clips_generated = db.query(Clip).filter(
            Clip.created_at >= start,
            Clip.created_at <= end
        ).count()
        
        clips_exported = db.query(Clip).filter(
            Clip.created_at >= start,
            Clip.created_at <= end,
            Clip.exported == True
        ).count()
        
        results.append(DailyStats(
            date=date.isoformat(),
            videos_processed=videos_processed,
            clips_generated=clips_generated,
            clips_exported=clips_exported
        ))
    
    return results

@router.get("/top-clips", response_model=List[TopClip])
def get_top_clips(limit: int = 10, db: Session = Depends(get_db)):
    """Get top clips by viral score"""
    clips = db.query(Clip).order_by(desc(Clip.viral_score)).limit(limit).all()
    
    return [TopClip(
        id=c.id,
        title=c.title,
        viral_score=c.viral_score,
        duration=c.duration,
        video_id=c.video_id,
        project_id=c.project_id,
        exported=c.exported,
        created_at=c.created_at
    ) for c in clips]

@router.get("/platform-stats", response_model=List[PlatformStats])
def get_platform_stats(db: Session = Depends(get_db)):
    """Get statistics by target platform"""
    stats = db.query(
        Project.target_platform,
        func.count(Clip.id).label('count'),
        func.avg(Clip.duration).label('avg_duration')
    ).join(Clip, Project.id == Clip.project_id).group_by(
        Project.target_platform
    ).all()
    
    return [PlatformStats(
        platform=s[0] or 'unknown',
        count=s[1],
        avg_duration=round(s[2] or 0, 2)
    ) for s in stats]

@router.get("/viral-distribution", response_model=List[ViralScoreDistribution])
def get_viral_distribution(db: Session = Depends(get_db)):
    """Get distribution of viral scores"""
    ranges = [
        ('0-2', 0, 2),
        ('2-4', 2, 4),
        ('4-6', 4, 6),
        ('6-8', 6, 8),
        ('8-10', 8, 10)
    ]
    
    results = []
    for label, min_score, max_score in ranges:
        count = db.query(Clip).filter(
            Clip.viral_score >= min_score,
            Clip.viral_score < max_score if max_score < 10 else Clip.viral_score <= max_score
        ).count()
        results.append(ViralScoreDistribution(range=label, count=count))
    
    return results

@router.get("/project/{project_id}/stats")
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    """Get statistics for a specific project"""
    videos = db.query(Video).filter(Video.project_id == project_id).all()
    clips = db.query(Clip).filter(Clip.project_id == project_id).all()
    
    total_duration = sum(v.duration or 0 for v in videos)
    clip_duration = sum(c.duration or 0 for c in clips)
    avg_viral = sum(c.viral_score for c in clips) / len(clips) if clips else 0
    exported_count = sum(1 for c in clips if c.exported)
    
    return {
        "project_id": project_id,
        "videos_count": len(videos),
        "clips_count": len(clips),
        "exported_count": exported_count,
        "total_video_duration": round(total_duration, 2),
        "total_clip_duration": round(clip_duration, 2),
        "avg_viral_score": round(avg_viral, 2),
        "compression_ratio": round((1 - clip_duration / total_duration) * 100, 1) if total_duration > 0 else 0
    }
