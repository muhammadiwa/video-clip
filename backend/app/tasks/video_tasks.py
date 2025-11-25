from celery import Task
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.video import Video
from app.models.clip import Clip
from app.services.video_processor import VideoProcessor
from app.services.youtube_downloader import YouTubeDownloader
from app.core.config import settings
from pathlib import Path
import traceback

class DatabaseTask(Task):
    """Base task with database session"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()

@celery_app.task(bind=True, base=DatabaseTask, name="process_uploaded_video")
def process_uploaded_video(self, video_id: int):
    """
    Process uploaded video: extract metadata, generate thumbnail, extract audio
    """
    try:
        # Update status
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        video.status = "processing"
        self.db.commit()
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Extracting video info...'}
        )
        
        # 1. Extract video metadata
        video_info = VideoProcessor.get_video_info(video.file_path)
        
        video.duration = video_info['duration']
        video.width = video_info['width']
        video.height = video_info['height']
        video.codec = video_info.get('codec')
        video.fps = video_info.get('fps')
        video.bitrate = video_info.get('bitrate')
        self.db.commit()
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Generating thumbnail...'}
        )
        
        # 2. Generate thumbnail
        thumbnail_dir = Path(settings.UPLOAD_DIR) / str(video.project_id) / "thumbnails"
        thumbnail_path = VideoProcessor.generate_thumbnail(
            video.file_path,
            str(thumbnail_dir),
            timestamp=min(1.0, video.duration / 2)
        )
        video.thumbnail_path = thumbnail_path
        self.db.commit()
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Extracting audio...'}
        )
        
        # 3. Extract audio for transcription
        audio_dir = Path(settings.TEMP_DIR) / str(video.project_id)
        audio_path = VideoProcessor.extract_audio(video.file_path, str(audio_dir))
        video.audio_path = audio_path
        self.db.commit()
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Video processing completed'}
        )
        
        # Update status to processed
        video.status = "processed"
        self.db.commit()
        
        return {
            'video_id': video_id,
            'status': 'success',
            'duration': video.duration,
            'resolution': f"{video.width}x{video.height}",
            'thumbnail': thumbnail_path,
            'audio': audio_path,
        }
        
    except Exception as e:
        # Update status to error
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "error"
            video.error_message = str(e)
            self.db.commit()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="download_youtube_video")
def download_youtube_video(self, project_id: int, youtube_url: str):
    """
    Download video from YouTube URL
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Validating YouTube URL...'}
        )
        
        # Validate URL
        if not YouTubeDownloader.is_valid_url(youtube_url):
            raise ValueError("Invalid YouTube URL")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Downloading video...'}
        )
        
        # Download video
        download_dir = Path(settings.UPLOAD_DIR) / str(project_id)
        result = YouTubeDownloader.download_video(youtube_url, str(download_dir))
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 70, 'total': 100, 'status': 'Creating database record...'}
        )
        
        # Create video record
        from app.models.project import Project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        video = Video(
            project_id=project_id,
            filename=Path(result['file_path']).name,
            original_filename=result['title'],
            file_path=result['file_path'],
            file_size=Path(result['file_path']).stat().st_size,
            duration=result['duration'],
            width=result['width'],
            height=result['height'],
            fps=result.get('fps'),
            source_type="youtube",
            source_url=youtube_url,
            status="downloaded"
        )
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Download completed'}
        )
        
        # Trigger video processing
        process_uploaded_video.delay(video.id)
        
        return {
            'video_id': video.id,
            'status': 'success',
            'title': result['title'],
            'duration': result['duration'],
            'file_path': result['file_path'],
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="trim_video_task")
def trim_video_task(self, video_id: int, start_time: float, end_time: float):
    """
    Trim video to specific time range
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Trimming video...'}
        )
        
        # Trim video
        output_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "trimmed"
        trimmed_path = VideoProcessor.trim_video(
            video.file_path,
            str(output_dir),
            start_time,
            end_time
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Trim completed'}
        )
        
        return {
            'video_id': video_id,
            'status': 'success',
            'trimmed_path': trimmed_path,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="compress_video_task")
def compress_video_task(self, video_id: int, crf: int = 28):
    """
    Compress video file
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Compressing video...'}
        )
        
        # Compress video
        output_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "compressed"
        compressed_path = VideoProcessor.compress_video(
            video.file_path,
            str(output_dir),
            crf=crf
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Compression completed'}
        )
        
        original_size = Path(video.file_path).stat().st_size
        compressed_size = Path(compressed_path).stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        return {
            'video_id': video_id,
            'status': 'success',
            'compressed_path': compressed_path,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': f"{compression_ratio:.1f}%",
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise
