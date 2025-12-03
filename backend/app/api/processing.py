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
    process_video_pipeline,
    export_clip_video,
    export_all_clips,
    detect_and_export_viral
)

router = APIRouter()

class ProcessVideoRequest(BaseModel):
    video_id: int

class YouTubeDownloadRequest(BaseModel):
    project_id: int
    youtube_url: str

class TranscribeRequest(BaseModel):
    video_id: int
    language: Optional[str] = None  # Source language (auto-detect if None)
    translate_to: Optional[str] = None  # Target language for translation (e.g., "en", "id", "es")

class DetectScenesRequest(BaseModel):
    video_id: int
    threshold: Optional[float] = 27.0
    use_ai: Optional[bool] = True  # Enable smart/AI-based detection

class DetectViralRequest(BaseModel):
    video_id: int
    top_n: Optional[int] = 5
    use_ai: Optional[bool] = True  # Enable OpenAI GPT-4 Vision analysis

class TrimVideoRequest(BaseModel):
    video_id: int
    start_time: float
    end_time: float

class CompressVideoRequest(BaseModel):
    video_id: int
    crf: Optional[int] = 28

class ExportClipRequest(BaseModel):
    clip_id: int
    target_platform: Optional[str] = "shorts"  # shorts, tiktok, reels
    aspect_ratio: Optional[str] = "9:16"

class ExportAllClipsRequest(BaseModel):
    video_id: int
    target_platform: Optional[str] = "shorts"
    aspect_ratio: Optional[str] = "9:16"

class DetectAndExportRequest(BaseModel):
    video_id: int
    top_n: Optional[int] = 5
    target_platform: Optional[str] = "shorts"
    aspect_ratio: Optional[str] = "9:16"
    burn_subtitles: Optional[bool] = True
    subtitle_style: Optional[str] = "viral_white"
    min_duration: Optional[float] = 30.0
    max_duration: Optional[float] = 60.0
    # Custom AI options
    title_tone: Optional[str] = "engaging"  # engaging, formal, casual, clickbait, professional
    custom_prompt: Optional[str] = None  # Custom prompt for title/description generation
    language: Optional[str] = "en"  # Output language for titles/descriptions


class BatchYouTubeDownloadRequest(BaseModel):
    project_id: int
    youtube_urls: list[str]


class BatchProcessRequest(BaseModel):
    video_ids: list[int]
    top_n: Optional[int] = 5
    target_platform: Optional[str] = "shorts"
    aspect_ratio: Optional[str] = "9:16"
    burn_subtitles: Optional[bool] = True
    subtitle_style: Optional[str] = "viral_white"
    min_duration: Optional[float] = 30.0
    max_duration: Optional[float] = 60.0


class BatchJobResponse(BaseModel):
    jobs: list[dict]
    message: str


class GenerateThumbnailRequest(BaseModel):
    clip_id: int
    frame_time: Optional[float] = None  # Specific time to capture, or None for AI selection
    add_text_overlay: Optional[bool] = False
    overlay_text: Optional[str] = None


class GenerateABTitlesRequest(BaseModel):
    clip_id: int
    num_variants: Optional[int] = 3  # Number of title variants to generate
    tone: Optional[str] = "engaging"  # engaging, clickbait, professional, casual
    language: Optional[str] = "en"


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
    Detect scenes in video using smart detection (AI/Fast methods)
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task with AI option
        task = detect_scenes.delay(request.video_id, request.threshold, request.use_ai)
        
        method = "AI/Smart detection" if request.use_ai else "Classic PySceneDetect"
        return JobResponse(
            job_id=task.id,
            status="started",
            message=f"Scene detection started ({method})"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-viral", response_model=JobResponse)
def trigger_viral_detection(request: DetectViralRequest, db: Session = Depends(get_db)):
    """
    Detect viral moments using AI (OpenAI GPT-4 Vision) or rule-based analysis
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task with AI option
        task = detect_viral_moments.delay(request.video_id, request.top_n, request.use_ai)
        
        method = "AI-powered (GPT-4 Vision)" if request.use_ai else "Rule-based"
        return JobResponse(
            job_id=task.id,
            status="started",
            message=f"Viral detection started ({method})"
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


@router.post("/export-clip", response_model=JobResponse)
def trigger_export_clip(request: ExportClipRequest, db: Session = Depends(get_db)):
    """
    Export a single clip to video file
    Optimized for social media platforms (Shorts, TikTok, Reels)
    """
    from app.models.clip import Clip
    
    try:
        clip = db.query(Clip).filter(Clip.id == request.clip_id).first()
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Trigger Celery task
        task = export_clip_video.delay(
            request.clip_id,
            request.target_platform,
            request.aspect_ratio
        )
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message=f"Exporting clip {request.clip_id} for {request.target_platform}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-all-clips", response_model=JobResponse)
def trigger_export_all_clips(request: ExportAllClipsRequest, db: Session = Depends(get_db)):
    """
    Export all clips for a video (batch export)
    Exports all detected viral clips to video files
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = export_all_clips.delay(
            request.video_id,
            request.target_platform,
            request.aspect_ratio
        )
        
        return JobResponse(
            job_id=task.id,
            status="started",
            message=f"Batch exporting all clips for video {request.video_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-and-export", response_model=JobResponse)
def trigger_detect_and_export(request: DetectAndExportRequest, db: Session = Depends(get_db)):
    """
    Complete viral clip workflow: detect viral moments AND export to video files WITH subtitles
    This is the recommended endpoint for end-to-end viral clip generation.
    
    Steps:
    1. Detect viral moments from scenes
    2. Create clip records in database
    3. Export each clip to video file with burned-in subtitles
    
    Subtitle Styles:
    - viral_white: White text with black outline (default)
    - viral_yellow: Yellow Impact font
    - mrbeast: Large Impact font (MrBeast style)
    - minimal: Clean, minimal style
    """
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Trigger Celery task
        task = detect_and_export_viral.delay(
            request.video_id,
            request.top_n,
            request.target_platform,
            request.aspect_ratio,
            request.burn_subtitles,
            request.subtitle_style,
            request.min_duration,
            request.max_duration
        )
        
        subtitle_info = f" with {request.subtitle_style} subtitles" if request.burn_subtitles else ""
        duration_info = f" ({request.min_duration:.0f}s-{request.max_duration:.0f}s)"
        return JobResponse(
            job_id=task.id,
            status="started",
            message=f"Detecting and exporting top {request.top_n} viral clips{duration_info} for {request.target_platform}{subtitle_info}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-download-youtube", response_model=BatchJobResponse)
def trigger_batch_youtube_download(request: BatchYouTubeDownloadRequest, db: Session = Depends(get_db)):
    """Download multiple videos from YouTube URLs"""
    try:
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        jobs = []
        for url in request.youtube_urls:
            task = download_youtube_video.delay(request.project_id, url)
            jobs.append({"job_id": task.id, "url": url, "status": "started"})
        
        return BatchJobResponse(
            jobs=jobs,
            message=f"Started downloading {len(jobs)} videos"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-process", response_model=BatchJobResponse)
def trigger_batch_process(request: BatchProcessRequest, db: Session = Depends(get_db)):
    """Process multiple videos with full pipeline (detect & export viral clips)"""
    try:
        jobs = []
        for video_id in request.video_ids:
            video = db.query(Video).filter(Video.id == video_id).first()
            if not video:
                jobs.append({"video_id": video_id, "job_id": None, "status": "error", "message": "Video not found"})
                continue
            
            task = detect_and_export_viral.delay(
                video_id,
                request.top_n,
                request.target_platform,
                request.aspect_ratio,
                request.burn_subtitles,
                request.subtitle_style,
                request.min_duration,
                request.max_duration
            )
            jobs.append({"video_id": video_id, "job_id": task.id, "status": "started"})
        
        successful = len([j for j in jobs if j["status"] == "started"])
        return BatchJobResponse(
            jobs=jobs,
            message=f"Started processing {successful}/{len(request.video_ids)} videos"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-thumbnail")
def generate_thumbnail(request: GenerateThumbnailRequest, db: Session = Depends(get_db)):
    """Generate thumbnail for a clip with optional text overlay"""
    from app.models.clip import Clip
    from app.services.video_processor import VideoProcessor
    from pathlib import Path
    
    try:
        clip = db.query(Clip).filter(Clip.id == request.clip_id).first()
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        video = db.query(Video).filter(Video.id == clip.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Determine capture time
        capture_time = request.frame_time
        if capture_time is None:
            # Default to 1/3 into the clip (often a good spot)
            capture_time = clip.start_time + (clip.duration / 3)
        
        # Generate thumbnail
        thumbnail_dir = Path(video.file_path).parent / "thumbnails"
        thumbnail_dir.mkdir(exist_ok=True)
        
        thumbnail_path = VideoProcessor.generate_thumbnail(
            video.file_path,
            str(thumbnail_dir),
            timestamp=capture_time,
            size=(1280, 720)
        )
        
        # Add text overlay if requested
        if request.add_text_overlay and request.overlay_text:
            import cv2
            img = cv2.imread(thumbnail_path)
            if img is not None:
                h, w = img.shape[:2]
                font = cv2.FONT_HERSHEY_DUPLEX
                font_scale = 1.5
                thickness = 3
                
                # Get text size
                text_size = cv2.getTextSize(request.overlay_text, font, font_scale, thickness)[0]
                x = (w - text_size[0]) // 2
                y = h - 50
                
                # Draw shadow
                cv2.putText(img, request.overlay_text, (x+2, y+2), font, font_scale, (0, 0, 0), thickness+2)
                # Draw text
                cv2.putText(img, request.overlay_text, (x, y), font, font_scale, (255, 255, 255), thickness)
                
                cv2.imwrite(thumbnail_path, img)
        
        return {
            "clip_id": clip.id,
            "thumbnail_path": thumbnail_path,
            "capture_time": capture_time,
            "message": "Thumbnail generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-ab-titles")
def generate_ab_titles(request: GenerateABTitlesRequest, db: Session = Depends(get_db)):
    """Generate multiple title variants for A/B testing using AI"""
    from app.models.clip import Clip
    from openai import OpenAI
    from app.core.config import settings
    
    try:
        clip = db.query(Clip).filter(Clip.id == request.clip_id).first()
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        tone_descriptions = {
            "engaging": "balanced, compelling, and attention-grabbing",
            "clickbait": "high-impact, curiosity-inducing, uses power words",
            "professional": "clean, credible, informative",
            "casual": "friendly, relatable, conversational",
            "formal": "business appropriate, authoritative"
        }
        
        tone_desc = tone_descriptions.get(request.tone, tone_descriptions["engaging"])
        
        prompt = f"""Generate {request.num_variants} different title variants for a viral video clip.

Context about the clip:
- Current title: {clip.title or 'Untitled'}
- Duration: {clip.duration:.1f} seconds
- Viral score: {clip.viral_score * 100:.0f}%

Requirements:
- Tone: {request.tone} ({tone_desc})
- Language: {request.language}
- Optimized for social media (YouTube Shorts, TikTok, Reels)
- Each title should be unique and test a different approach
- Keep titles under 60 characters for best display

Return as JSON array:
[
  {{"title": "...", "approach": "brief description of approach", "predicted_ctr": 0.0-1.0}},
  ...
]"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.8
        )
        
        import json
        content = response.choices[0].message.content
        start = content.find('[')
        end = content.rfind(']') + 1
        variants = json.loads(content[start:end]) if start >= 0 and end > start else []
        
        return {
            "clip_id": clip.id,
            "original_title": clip.title,
            "variants": variants,
            "tone": request.tone,
            "language": request.language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
