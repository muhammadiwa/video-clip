from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.core.database import get_db
from app.models.video import Video
from app.models.project import Project
from app.tasks.video_tasks import (
    process_uploaded_video,
    download_youtube_video,
    trim_video_task,
    compress_video_task
)
from app.tasks.ai_tasks import (
    transcribe_video,
    detect_scenes,
    detect_viral_moments,
    process_video_pipeline
)

router = APIRouter()

class ProcessVideoRequest(BaseModel):
    video_id: int

class YouTubeDownloadRequest(BaseModel):
    project_id: int
    youtube_url: str

class TranscribeRequest(BaseModel):
    video_id: int
    language: Optional[str] = None

class DetectScenesRequest(BaseModel):
    video_id: int
    threshold: Optional[float] = 27.0

class DetectViralRequest(BaseModel):
    video_id: int
    top_n: Optional[int] = 5

class TrimVideoRequest(BaseModel):
    video_id: int
    start_time: float
    end_time: float

class CompressVideoRequest(BaseModel):
    video_id: int
    crf: Optional[int] = 28

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/process-video", response_model=JobResponse)
def trigger_process_video(request: ProcessVideoRequest, db: Session = Depends(get_db)):
    """
    Trigger video processing (extract metadata, thumbnail, audio)
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = process_uploaded_video.delay(request.video_id)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="Video processing started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download-youtube", response_model=JobResponse)
def trigger_youtube_download(request: YouTubeDownloadRequest, db: Session = Depends(get_db)):
    """
    Download video from YouTube URL
    """
    try:
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Trigger Celery task
        task = download_youtube_video.delay(request.project_id, request.youtube_url)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="YouTube download started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe", response_model=JobResponse)
def trigger_transcription(request: TranscribeRequest, db: Session = Depends(get_db)):
    """
    Transcribe video using OpenAI Whisper
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = transcribe_video.delay(request.video_id, request.language)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="Video transcription started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-scenes", response_model=JobResponse)
def trigger_scene_detection(request: DetectScenesRequest, db: Session = Depends(get_db)):
    """
    Detect scenes in video
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = detect_scenes.delay(request.video_id, request.threshold)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="Scene detection started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-viral", response_model=JobResponse)
def trigger_viral_detection(request: DetectViralRequest, db: Session = Depends(get_db)):
    """
    Detect viral moments in video
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = detect_viral_moments.delay(request.video_id, request.top_n)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="Viral moment detection started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-pipeline", response_model=JobResponse)
def trigger_full_pipeline(request: ProcessVideoRequest, db: Session = Depends(get_db)):
    """
    Run full video processing pipeline:
    1. Process video (metadata, thumbnail, audio)
    2. Transcribe audio
    3. Detect scenes
    4. Detect viral moments
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task pipeline
        task = process_video_pipeline.delay(request.video_id)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="Full processing pipeline started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trim-video", response_model=JobResponse)
def trigger_trim_video(request: TrimVideoRequest, db: Session = Depends(get_db)):
    """
    Trim video to specific time range
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = trim_video_task.delay(request.video_id, request.start_time, request.end_time)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="Video trimming started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compress-video", response_model=JobResponse)
def trigger_compress_video(request: CompressVideoRequest, db: Session = Depends(get_db)):
    """
    Compress video file
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = compress_video_task.delay(request.video_id, request.crf)
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message="Video compression started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
