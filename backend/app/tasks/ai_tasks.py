from celery import Task, chain
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.video import Video
from app.models.clip import Clip
from app.models.subtitle import Subtitle
from app.services.transcription import TranscriptionService
from app.services.ai_scene_detector import SmartSceneDetector as SceneDetector
from app.services.ai_viral_detector import HybridViralDetector as ViralDetector
from app.services.video_processor import VideoProcessor
from app.core.config import settings
from pathlib import Path
import json
import traceback
import numpy as np
from openai import OpenAI


def sanitize_for_json(obj):
    """Convert numpy types and other non-serializable types to native Python types"""
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(x) for x in obj]
    return obj


def generate_clip_metadata(transcription_text: str, viral_score: float, duration: float, clip_index: int) -> dict:
    """
    Generate AI-powered title and description for a clip
    
    Args:
        transcription_text: The transcription text for this clip
        viral_score: The viral potential score (0-1)
        duration: Clip duration in seconds
        clip_index: Index of the clip (1-based)
        
    Returns:
        dict with 'title' and 'description' keys
    """
    try:
        if not settings.OPENAI_API_KEY:
            return {
                'title': f"Viral Moment #{clip_index}",
                'description': f"A {duration:.0f}s clip with {viral_score*100:.0f}% viral potential"
            }
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""Based on this transcript from a video clip, generate a catchy title and description for social media (TikTok, YouTube Shorts, Instagram Reels).

Transcript: "{transcription_text[:500]}"

Viral Score: {viral_score*100:.0f}%
Duration: {duration:.0f} seconds

Requirements:
- Title: 5-10 words, catchy, creates curiosity, NO hashtags
- Description: 1-2 sentences describing what happens, engaging tone

Respond in JSON format:
{{"title": "your title here", "description": "your description here"}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        # Parse JSON from response
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(result_text[start:end])
            return {
                'title': result.get('title', f"Viral Moment #{clip_index}"),
                'description': result.get('description', '')
            }
    except Exception as e:
        print(f"[WARNING] Failed to generate clip metadata: {e}")
    
    return {
        'title': f"Viral Moment #{clip_index}",
        'description': f"A {duration:.0f}s clip with {viral_score*100:.0f}% viral potential"
    }

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
        # Let Celery handle the exception properly
        print(f"[ERROR] Task failed: {str(e)}")
        print(traceback.format_exc())
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="detect_scenes")
def detect_scenes(self, video_id: int, threshold: float = 27.0, use_ai: bool = True):
    """
    Detect scenes in video using SMART DETECTION (AI or Fast methods)
    Auto-selects best method based on video length and hardware
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Selecting detection method...'}
        )
        
        # Always use Smart AI-based scene detection
        def progress_callback(progress, status):
            self.update_state(
                state='PROGRESS',
                meta={'current': int(20 + progress * 70), 'total': 100, 'status': status}
            )
        
        print(f"[SMART] Using intelligent scene detection for {video.duration:.0f}s video")
        # Note: detect_scenes now automatically analyzes complexity
        analyzed_scenes = SceneDetector.detect_scenes(
            video.file_path,
            video.duration,
            progress_callback=progress_callback
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Scene analysis complete'}
        )
        
        # Save scenes to file
        scenes_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "scenes"
        scenes_dir.mkdir(parents=True, exist_ok=True)
        scenes_path = scenes_dir / f"video_{video_id}_scenes.json"
        
        with open(scenes_path, 'w') as f:
            json.dump(analyzed_scenes, f, indent=2)
        
        # Update video record with scenes info
        video.scenes_path = str(scenes_path)
        video.has_scenes = True
        self.db.commit()
        
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
        # Let Celery handle the exception properly
        print(f"[ERROR] Task failed: {str(e)}")
        print(traceback.format_exc())
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="detect_viral_moments")
def detect_viral_moments(self, video_id: int, top_n: int = 5, use_ai: bool = True):
    """
    Detect viral moments using AI (OpenAI GPT-4 Vision) or rule-based analysis
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
            meta={'current': 50, 'total': 100, 'status': 'Analyzing viral potential with AI...'}
        )
        
        # Use Hybrid AI-based viral detection (with fallback)
        print("[AI] Using Hybrid Viral Detection (AI + Rules)")
        
        try:
            detector = ViralDetector(use_ai=use_ai)
            top_moments = detector.detect_viral_moments(
                video.file_path,
                scenes,
                transcription,
                top_n=top_n
            )
            
            print(f"[AI] Found {len(top_moments)} viral moments")
            
        except Exception as e:
            print(f"[WARNING] Viral detection error: {e}, using basic algorithm")
            # Emergency fallback - use scene scores directly
            scored_scenes = sorted(scenes, key=lambda x: x.get('complexity_score', 0), reverse=True)
            top_moments = scored_scenes[:top_n]
            
            # Add basic viral scores
            for i, moment in enumerate(top_moments):
                if 'viral_score' not in moment:
                    moment['viral_score'] = 0.6 + (i * -0.05)  # Decreasing scores
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 85, 'total': 100, 'status': 'Creating clip records...'}
        )
        
        # Create clip records in database
        created_clips = []
        for i, moment in enumerate(top_moments):
            # Generate clip metadata (built-in simple metadata)
            metadata = {
                'viral_score': moment.get('viral_score', 0),
                'complexity_score': moment.get('complexity_score', 0),
                'action_level': moment.get('action_level', 'unknown'),
                'reasoning': moment.get('reasoning', 'Detected by AI viral detection'),
                'categories': moment.get('categories', []),
                'hook_potential': moment.get('hook_potential', 0.5),
            }
            
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
        
        # Save viral moments to file (sanitize numpy types for JSON serialization)
        viral_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "viral_moments"
        viral_dir.mkdir(parents=True, exist_ok=True)
        viral_path = viral_dir / f"video_{video_id}_viral_moments.json"
        
        sanitized_moments = sanitize_for_json(top_moments)
        with open(viral_path, 'w') as f:
            json.dump(sanitized_moments, f, indent=2)
        
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
        # Let Celery handle the exception properly
        print(f"[ERROR] Task failed: {str(e)}")
        print(traceback.format_exc())
        raise

@celery_app.task(bind=True, base=DatabaseTask, name="export_clip_video")
def export_clip_video(self, clip_id: int, target_platform: str = "shorts", aspect_ratio: str = "9:16"):
    """
    Export a single clip to video file
    """
    try:
        clip = self.db.query(Clip).filter(Clip.id == clip_id).first()
        if not clip:
            raise ValueError(f"Clip {clip_id} not found")
        
        video = self.db.query(Video).filter(Video.id == clip.video_id).first()
        if not video:
            raise ValueError(f"Video {clip.video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': f'Exporting clip {clip_id}...'}
        )
        
        # Create export directory
        export_dir = Path(settings.UPLOAD_DIR) / str(clip.project_id) / "clips"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate clip name
        clip_name = clip.title or clip.name or f"clip_{clip_id}"
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Processing video with FFmpeg...'}
        )
        
        # Export clip using VideoProcessor
        export_path = VideoProcessor.export_viral_clip(
            video_path=video.file_path,
            output_dir=str(export_dir),
            start_time=clip.start_time,
            end_time=clip.end_time,
            clip_name=clip_name,
            target_platform=target_platform,
            aspect_ratio=aspect_ratio
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Updating database...'}
        )
        
        # Update clip record
        clip.export_path = export_path
        clip.exported = True
        clip.status = "exported"
        clip.aspect_ratio = aspect_ratio
        self.db.commit()
        
        # Get file size
        file_size = Path(export_path).stat().st_size
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Export completed'}
        )
        
        return {
            'clip_id': clip_id,
            'status': 'success',
            'export_path': export_path,
            'file_size': file_size,
            'duration': clip.duration,
            'aspect_ratio': aspect_ratio,
        }
        
    except Exception as e:
        print(f"[ERROR] Export clip failed: {str(e)}")
        print(traceback.format_exc())
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="export_all_clips")
def export_all_clips(self, video_id: int, target_platform: str = "shorts", aspect_ratio: str = "9:16"):
    """
    Export all clips for a video (batch export)
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        # Get all clips for this video
        clips = self.db.query(Clip).filter(Clip.video_id == video_id).order_by(Clip.viral_score.desc()).all()
        
        if not clips:
            return {
                'video_id': video_id,
                'status': 'success',
                'message': 'No clips to export',
                'exported_count': 0,
                'clips': []
            }
        
        total_clips = len(clips)
        exported_clips = []
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 5, 'total': 100, 'status': f'Exporting {total_clips} clips...'}
        )
        
        # Create export directory
        export_dir = Path(settings.UPLOAD_DIR) / str(video.project_id) / "clips"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        for i, clip in enumerate(clips):
            progress = int(10 + (i / total_clips) * 85)
            
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': progress,
                    'total': 100,
                    'status': f'Exporting clip {i+1}/{total_clips}: {clip.title or f"Clip #{i+1}"}'
                }
            )
            
            try:
                # Generate clip name
                clip_name = clip.title or clip.name or f"clip_{clip.id}"
                
                # Export clip
                export_path = VideoProcessor.export_viral_clip(
                    video_path=video.file_path,
                    output_dir=str(export_dir),
                    start_time=clip.start_time,
                    end_time=clip.end_time,
                    clip_name=clip_name,
                    target_platform=target_platform,
                    aspect_ratio=aspect_ratio
                )
                
                # Update clip record
                clip.export_path = export_path
                clip.exported = True
                clip.status = "exported"
                clip.aspect_ratio = aspect_ratio
                self.db.commit()
                
                file_size = Path(export_path).stat().st_size
                
                exported_clips.append({
                    'clip_id': clip.id,
                    'title': clip.title,
                    'export_path': export_path,
                    'file_size': file_size,
                    'duration': clip.duration,
                    'viral_score': clip.viral_score,
                })
                
                print(f"[EXPORT] Clip {clip.id} exported: {export_path}")
                
            except Exception as e:
                print(f"[ERROR] Failed to export clip {clip.id}: {e}")
                exported_clips.append({
                    'clip_id': clip.id,
                    'title': clip.title,
                    'error': str(e),
                    'status': 'failed'
                })
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': f'Exported {len([c for c in exported_clips if "error" not in c])} clips'}
        )
        
        successful = len([c for c in exported_clips if 'error' not in c])
        failed = len([c for c in exported_clips if 'error' in c])
        
        return {
            'video_id': video_id,
            'status': 'success',
            'total_clips': total_clips,
            'exported_count': successful,
            'failed_count': failed,
            'export_dir': str(export_dir),
            'clips': exported_clips,
        }
        
    except Exception as e:
        print(f"[ERROR] Batch export failed: {str(e)}")
        print(traceback.format_exc())
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="process_video_pipeline")
def process_video_pipeline(self, video_id: int):
    """
    Full video processing pipeline:
    1. Transcribe audio
    2. Detect scenes
    3. Detect viral moments
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting AI pipeline...'}
        )
        
        # Execute pipeline as chain of tasks
        # Use .si() (immutable signature) to pass video_id explicitly
        pipeline = chain(
            transcribe_video.si(video_id),
            detect_scenes.si(video_id),
            detect_viral_moments.si(video_id, top_n=5),
        )
        
        result = pipeline.apply_async()
        
        return {
            'video_id': video_id,
            'status': 'pipeline_started',
            'task_id': result.id,
        }
        
    except Exception as e:
        # Let Celery handle the exception properly
        print(f"[ERROR] Task failed: {str(e)}")
        print(traceback.format_exc())
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="detect_and_export_viral")
def detect_and_export_viral(
    self, 
    video_id: int, 
    top_n: int = 5, 
    target_platform: str = "shorts", 
    aspect_ratio: str = "9:16",
    burn_subtitles: bool = True,
    subtitle_style: str = "viral_white",
    min_duration: float = 30.0,
    max_duration: float = 60.0
):
    """
    Complete viral clip workflow:
    1. Detect viral moments
    2. Create clip records
    3. Export all clips to video files WITH subtitles burned in
    
    This is the recommended task for end-to-end viral clip generation.
    
    Args:
        video_id: ID of the video
        top_n: Number of top viral clips to generate
        target_platform: Target platform (shorts, tiktok, reels)
        aspect_ratio: Target aspect ratio (9:16, 16:9, 1:1)
        burn_subtitles: Whether to burn subtitles into video (default True)
        subtitle_style: Style preset (viral_white, viral_yellow, mrbeast, minimal)
        min_duration: Minimum clip duration in seconds (default 30)
        max_duration: Maximum clip duration in seconds (default 60)
    """
    try:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 5, 'total': 100, 'status': 'Loading scene data...'}
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
            meta={'current': 10, 'total': 100, 'status': 'Loading transcription...'}
        )
        
        # Load transcription (if available)
        transcription = None
        subtitles_data = []
        if video.transcription_path and Path(video.transcription_path).exists():
            with open(video.transcription_path, 'r') as f:
                transcription = json.load(f)
            # Extract subtitle segments for burning
            if transcription and 'segments' in transcription:
                subtitles_data = [
                    {
                        'start_time': seg['start'],
                        'end_time': seg['end'],
                        'text': seg['text']
                    }
                    for seg in transcription['segments']
                ]
                print(f"[SUBTITLE] Loaded {len(subtitles_data)} subtitle segments")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 15, 'total': 100, 'status': 'Detecting viral moments...'}
        )
        
        # Detect viral moments with custom duration settings
        try:
            detector = ViralDetector(use_ai=True)
            top_moments = detector.detect_viral_moments(
                video.file_path,
                scenes,
                transcription,
                top_n=top_n,
                min_duration=min_duration,
                target_duration=(min_duration + max_duration) / 2,  # Target middle of range
                max_duration=max_duration
            )
            print(f"[AI] Found {len(top_moments)} viral moments (duration: {min_duration:.0f}s-{max_duration:.0f}s)")
        except Exception as e:
            print(f"[WARNING] Viral detection error: {e}, using basic algorithm")
            scored_scenes = sorted(scenes, key=lambda x: x.get('complexity_score', 0), reverse=True)
            top_moments = scored_scenes[:top_n]
            for i, moment in enumerate(top_moments):
                if 'viral_score' not in moment:
                    moment['viral_score'] = 0.6 + (i * -0.05)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Creating clip records...'}
        )
        
        # Create export directory
        export_dir = Path(settings.UPLOAD_DIR) / str(video.project_id) / "clips"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Get subtitle style
        style_presets = VideoProcessor.get_default_subtitle_styles()
        selected_style = style_presets.get(subtitle_style, style_presets['viral_white'])
        
        # Create clips and export
        created_clips = []
        total_moments = len(top_moments)
        
        for i, moment in enumerate(top_moments):
            progress = int(35 + (i / total_moments) * 60)
            
            subtitle_status = "with subtitles" if burn_subtitles and subtitles_data else "without subtitles"
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': progress,
                    'total': 100,
                    'status': f'Exporting clip {i+1}/{total_moments} ({subtitle_status})...'
                }
            )
            
            # Get transcription text for this clip to generate AI title/description
            clip_start = moment['start_time']
            clip_end = moment['end_time']
            clip_text = ""
            if transcription and 'segments' in transcription:
                clip_segments = [
                    seg['text'] for seg in transcription['segments']
                    if seg['start'] >= clip_start and seg['end'] <= clip_end
                ]
                clip_text = " ".join(clip_segments)
            
            # Generate AI title and description
            print(f"[AI] Generating title/description for clip {i+1}...")
            metadata = generate_clip_metadata(
                transcription_text=clip_text,
                viral_score=moment['viral_score'],
                duration=moment['duration'],
                clip_index=i + 1
            )
            
            # Create clip record with AI-generated metadata
            clip = Clip(
                video_id=video_id,
                project_id=video.project_id,
                start_time=moment['start_time'],
                end_time=moment['end_time'],
                duration=moment['duration'],
                viral_score=moment['viral_score'],
                title=metadata['title'],
                description=metadata['description'],
                status="exporting",
                aspect_ratio=aspect_ratio,
                subtitle_style={'preset': subtitle_style, **selected_style} if burn_subtitles else None
            )
            self.db.add(clip)
            self.db.commit()
            self.db.refresh(clip)
            
            try:
                # Export clip
                clip_name = f"viral_clip_{i+1}_score_{int(moment['viral_score']*100)}"
                
                # Choose export method based on subtitle availability
                if burn_subtitles and subtitles_data:
                    export_path = VideoProcessor.export_viral_clip_with_subtitles(
                        video_path=video.file_path,
                        output_dir=str(export_dir),
                        start_time=clip.start_time,
                        end_time=clip.end_time,
                        subtitles=subtitles_data,
                        clip_name=clip_name,
                        target_platform=target_platform,
                        aspect_ratio=aspect_ratio,
                        subtitle_style=selected_style
                    )
                else:
                    export_path = VideoProcessor.export_viral_clip(
                        video_path=video.file_path,
                        output_dir=str(export_dir),
                        start_time=clip.start_time,
                        end_time=clip.end_time,
                        clip_name=clip_name,
                        target_platform=target_platform,
                        aspect_ratio=aspect_ratio
                    )
                
                # Update clip with export info
                clip.export_path = export_path
                clip.exported = True
                clip.status = "exported"
                self.db.commit()
                
                file_size = Path(export_path).stat().st_size
                
                created_clips.append({
                    'clip_id': clip.id,
                    'start_time': clip.start_time,
                    'end_time': clip.end_time,
                    'duration': clip.duration,
                    'viral_score': clip.viral_score,
                    'export_path': export_path,
                    'file_size': file_size,
                    'has_subtitles': burn_subtitles and bool(subtitles_data),
                    'status': 'exported'
                })
                
                print(f"[EXPORT] Clip {clip.id} exported successfully: {export_path}")
                
            except Exception as e:
                clip.status = "export_failed"
                self.db.commit()
                
                created_clips.append({
                    'clip_id': clip.id,
                    'start_time': clip.start_time,
                    'end_time': clip.end_time,
                    'duration': clip.duration,
                    'viral_score': clip.viral_score,
                    'error': str(e),
                    'status': 'export_failed'
                })
                print(f"[ERROR] Failed to export clip {clip.id}: {e}")
        
        # Save viral moments to file (sanitize numpy types for JSON serialization)
        viral_dir = Path(settings.TEMP_DIR) / str(video.project_id) / "viral_moments"
        viral_dir.mkdir(parents=True, exist_ok=True)
        viral_path = viral_dir / f"video_{video_id}_viral_moments.json"
        
        sanitized_moments = sanitize_for_json(top_moments)
        with open(viral_path, 'w') as f:
            json.dump(sanitized_moments, f, indent=2)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'All clips exported successfully'}
        )
        
        successful = len([c for c in created_clips if c['status'] == 'exported'])
        failed = len([c for c in created_clips if c['status'] == 'export_failed'])
        
        return {
            'video_id': video_id,
            'status': 'success',
            'total_moments': len(top_moments),
            'clips_exported': successful,
            'clips_failed': failed,
            'subtitles_burned': burn_subtitles and bool(subtitles_data),
            'subtitle_style': subtitle_style,
            'export_dir': str(export_dir),
            'viral_moments_path': str(viral_path),
            'clips': created_clips,
        }
        
    except Exception as e:
        print(f"[ERROR] Detect and export failed: {str(e)}")
        print(traceback.format_exc())
        raise
