from celery import Task, chain
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.video import Video
from app.models.clip import Clip
from app.models.subtitle import Subtitle
from app.services.transcription import TranscriptionService
from app.services.scene_detector import SceneDetector
from app.services.viral_detector import ViralMomentDetector
from app.core.config import settings
from pathlib import Path
import json
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

@celery_app.task(bind=True, base=DatabaseTask, name="transcribe_video")
def transcribe_video(self, video_id: int, language: str = None):
    """
    Transcribe video using OpenAI Whisper
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Loading Whisper model...'}
        )
        
        # Initialize transcription service
        transcription_service = TranscriptionService(model_name="base")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Transcribing audio...'}
        )
        
        # Transcribe video
        audio_path = video.audio_path if video.audio_path else video.file_path
        transcription = transcription_service.transcribe_audio(
            audio_path,
            language=language
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 70, 'total': 100, 'status': 'Saving transcription...'}
        )
        
        # Save transcription to file
        transcription_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "transcriptions"
        transcription_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = transcription_dir / f"video_{video_id}_transcription.json"
        transcription_service.save_transcription(transcription, str(json_path), format="json")
        
        # Save SRT
        srt_path = transcription_dir / f"video_{video_id}_subtitles.srt"
        transcription_service.save_transcription(transcription, str(srt_path), format="srt")
        
        # Save VTT
        vtt_path = transcription_dir / f"video_{video_id}_subtitles.vtt"
        transcription_service.save_transcription(transcription, str(vtt_path), format="vtt")
        
        # Update video record
        video.transcription_path = str(json_path)
        video.has_transcription = True
        self.db.commit()
        
        # Create subtitle records
        for segment in transcription['segments']:
            subtitle = Subtitle(
                video_id=video_id,
                start_time=segment['start'],
                end_time=segment['end'],
                text=segment['text'],
                language=transcription['language']
            )
            self.db.add(subtitle)
        
        self.db.commit()
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Transcription completed'}
        )
        
        # Extract keywords
        keywords = transcription_service.extract_keywords(transcription, top_n=10)
        
        return {
            'video_id': video_id,
            'status': 'success',
            'language': transcription['language'],
            'duration': transcription['duration'],
            'segment_count': len(transcription['segments']),
            'transcription_path': str(json_path),
            'srt_path': str(srt_path),
            'vtt_path': str(vtt_path),
            'keywords': keywords,
            'text_preview': transcription['text'][:200] + '...' if len(transcription['text']) > 200 else transcription['text']
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="detect_scenes")
def detect_scenes(self, video_id: int, threshold: float = 27.0):
    """
    Detect scenes in video using PySceneDetect
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Detecting scenes...'}
        )
        
        # Detect scenes
        scenes = SceneDetector.detect_scenes(
            video.file_path,
            threshold=threshold,
            min_scene_len=1.0
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 60, 'total': 100, 'status': 'Analyzing scene complexity...'}
        )
        
        # Analyze scene complexity
        analyzed_scenes = SceneDetector.analyze_scene_complexity(scenes)
        
        # Save scenes to file
        scenes_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "scenes"
        scenes_dir.mkdir(parents=True, exist_ok=True)
        scenes_path = scenes_dir / f"video_{video_id}_scenes.json"
        
        with open(scenes_path, 'w') as f:
            json.dump(analyzed_scenes, f, indent=2)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Scene detection completed'}
        )
        
        return {
            'video_id': video_id,
            'status': 'success',
            'scene_count': len(analyzed_scenes),
            'scenes_path': str(scenes_path),
            'scenes': analyzed_scenes,
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="detect_viral_moments")
def detect_viral_moments(self, video_id: int, top_n: int = 5):
    """
    Detect viral moments in video based on scenes and transcription
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Loading scene data...'}
        )
        
        # Load scenes
        scenes_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "scenes"
        scenes_path = scenes_dir / f"video_{video_id}_scenes.json"
        
        if not scenes_path.exists():
            raise ValueError("Scenes data not found. Run scene detection first.")
        
        with open(scenes_path, 'r') as f:
            scenes = json.load(f)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Loading transcription...'}
        )
        
        # Load transcription (if available)
        transcription = None
        if video.transcription_path and Path(video.transcription_path).exists():
            with open(video.transcription_path, 'r') as f:
                transcription = json.load(f)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Calculating viral scores...'}
        )
        
        # Calculate viral scores
        scored_scenes = ViralMomentDetector.calculate_viral_score(
            scenes,
            transcription=transcription,
            video_info={'duration': video.duration, 'width': video.width, 'height': video.height}
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 70, 'total': 100, 'status': 'Filtering top viral moments...'}
        )
        
        # Filter top viral moments
        top_moments = ViralMomentDetector.filter_top_viral_moments(
            scored_scenes,
            top_n=top_n,
            min_score=0.5
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 85, 'total': 100, 'status': 'Creating clip records...'}
        )
        
        # Create clip records in database
        created_clips = []
        for i, moment in enumerate(top_moments):
            # Generate clip metadata
            metadata = ViralMomentDetector.generate_clip_metadata(moment, transcription)
            
            clip = Clip(
                video_id=video_id,
                project_id=video.project_id,
                start_time=moment['start_time'],
                end_time=moment['end_time'],
                duration=moment['duration'],
                viral_score=moment['viral_score'],
                title=f"Viral Clip #{i+1}",
                status="detected"
            )
            self.db.add(clip)
            self.db.commit()
            self.db.refresh(clip)
            
            created_clips.append({
                'clip_id': clip.id,
                'start_time': clip.start_time,
                'end_time': clip.end_time,
                'duration': clip.duration,
                'viral_score': clip.viral_score,
                'metadata': metadata,
            })
        
        # Save viral moments to file
        viral_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "viral_moments"
        viral_dir.mkdir(parents=True, exist_ok=True)
        viral_path = viral_dir / f"video_{video_id}_viral_moments.json"
        
        with open(viral_path, 'w') as f:
            json.dump(top_moments, f, indent=2)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Viral moment detection completed'}
        )
        
        return {
            'video_id': video_id,
            'status': 'success',
            'total_moments': len(top_moments),
            'clips_created': len(created_clips),
            'viral_moments_path': str(viral_path),
            'clips': created_clips,
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="process_video_pipeline")
def process_video_pipeline(self, video_id: int):
    """
    Full video processing pipeline:
    1. Process video (metadata, thumbnail, audio)
    2. Transcribe audio
    3. Detect scenes
    4. Detect viral moments
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting pipeline...'}
        )
        
        # Execute pipeline as chain of tasks
        pipeline = chain(
            transcribe_video.s(video_id),
            detect_scenes.s(video_id),
            detect_viral_moments.s(video_id),
        )
        
        result = pipeline.apply_async()
        
        return {
            'video_id': video_id,
            'status': 'pipeline_started',
            'task_id': result.id,
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise
