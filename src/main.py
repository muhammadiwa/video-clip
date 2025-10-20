"""Main application for Viral Clip AI Generator."""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from src.downloader.youtube import YouTubeDownloader
from src.processor.scene_detector import SceneDetector
from src.processor.video_editor import VideoEditor
from src.generator.content_generator import ContentGenerator
from src.generator.subtitle_generator import SubtitleGenerator
from src.utils.config import Config
from src.utils.logger import logger


class ViralClipGenerator:
    """Main class for generating viral clips from videos."""
    
    def __init__(self):
        """Initialize the viral clip generator."""
        Config.ensure_directories()
        
        # Use temp directory for downloads
        temp_dir = tempfile.gettempdir()
        self.downloader = YouTubeDownloader(output_dir=os.path.join(temp_dir, "viral_clip_videos"))
        self.scene_detector = SceneDetector()
        self.video_editor = VideoEditor()
        self.content_generator = ContentGenerator()
        self.subtitle_generator = SubtitleGenerator(model_name="base")
        
        logger.info("Viral Clip Generator initialized")
    
    def process_youtube_video(
        self,
        url: str,
        num_clips: int = 3,
        clip_duration: Optional[int] = None,
        generate_subtitles: bool = True,
        generate_content: bool = True
    ) -> List[dict]:
        """Process a YouTube video and generate viral clips.
        
        Args:
            url: YouTube video URL
            num_clips: Number of clips to generate
            clip_duration: Target clip duration (None for auto)
            generate_subtitles: Whether to generate subtitles
            generate_content: Whether to generate viral content
            
        Returns:
            List of generated clip information dictionaries
        """
        logger.info(f"Processing YouTube video: {url}")
        
        # Download video
        video_info = self.downloader.download(url)
        video_path = video_info['path']
        
        # Process the video
        return self._process_video(
            video_path=video_path,
            video_info=video_info,
            num_clips=num_clips,
            clip_duration=clip_duration,
            generate_subtitles=generate_subtitles,
            generate_content=generate_content
        )
    
    def process_local_video(
        self,
        video_path: str,
        num_clips: int = 3,
        clip_duration: Optional[int] = None,
        generate_subtitles: bool = True,
        generate_content: bool = True
    ) -> List[dict]:
        """Process a local video file and generate viral clips.
        
        Args:
            video_path: Path to local video file
            num_clips: Number of clips to generate
            clip_duration: Target clip duration (None for auto)
            generate_subtitles: Whether to generate subtitles
            generate_content: Whether to generate viral content
            
        Returns:
            List of generated clip information dictionaries
        """
        logger.info(f"Processing local video: {video_path}")
        
        # Get basic video info
        video_info = self.video_editor.get_video_info(video_path)
        video_info['title'] = Path(video_path).stem
        video_info['description'] = ''
        video_info['path'] = video_path
        
        # Process the video
        return self._process_video(
            video_path=video_path,
            video_info=video_info,
            num_clips=num_clips,
            clip_duration=clip_duration,
            generate_subtitles=generate_subtitles,
            generate_content=generate_content
        )
    
    def _process_video(
        self,
        video_path: str,
        video_info: dict,
        num_clips: int,
        clip_duration: Optional[int],
        generate_subtitles: bool,
        generate_content: bool
    ) -> List[dict]:
        """Internal method to process a video.
        
        Args:
            video_path: Path to video file
            video_info: Video information dictionary
            num_clips: Number of clips to generate
            clip_duration: Target clip duration
            generate_subtitles: Whether to generate subtitles
            generate_content: Whether to generate viral content
            
        Returns:
            List of generated clip information dictionaries
        """
        results = []
        
        # Detect scenes
        logger.info("Detecting scenes in video...")
        scenes = self.scene_detector.detect_scenes(video_path)
        
        if not scenes:
            logger.warning("No scenes detected, using simple time-based splits")
            scenes = self._create_time_based_scenes(video_info.get('duration', 300))
        
        # Get best moments
        logger.info("Identifying best moments...")
        best_moments = self.scene_detector.get_best_moments(
            scenes,
            min_duration=clip_duration or Config.MIN_CLIP_DURATION,
            max_duration=clip_duration or Config.MAX_CLIP_DURATION,
            num_clips=num_clips
        )
        
        if not best_moments:
            logger.warning("No suitable moments found, using fallback")
            best_moments = self._create_fallback_moments(
                video_info.get('duration', 300),
                num_clips
            )
        
        # Generate clips
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, (start_time, end_time) in enumerate(best_moments, 1):
            logger.info(f"Processing clip {i}/{len(best_moments)}")
            
            # Generate clip filename
            clip_name = f"clip_{timestamp}_{i}"
            clip_path = str(Config.CLIP_DIR / f"{clip_name}.mp4")
            
            # Extract clip
            logger.info(f"Extracting clip {i}...")
            self.video_editor.extract_clip(
                video_path,
                start_time,
                end_time,
                clip_path,
                convert_to_shorts=True
            )
            
            # Extract thumbnail
            logger.info(f"Extracting thumbnail for clip {i}...")
            thumbnail_time = (start_time + end_time) / 2
            thumbnail_path = self.video_editor.extract_thumbnail(
                clip_path,
                time=(end_time - start_time) / 2,
                output_path=str(Config.THUMBNAIL_DIR / f"{clip_name}_thumb.jpg")
            )
            
            # Generate subtitles
            subtitle_path = None
            transcript = ""
            if generate_subtitles:
                try:
                    logger.info(f"Generating subtitles for clip {i}...")
                    subtitle_path = self.subtitle_generator.generate_subtitles(
                        clip_path,
                        output_path=str(Config.CLIP_DIR / f"{clip_name}.srt")
                    )
                    transcript = self.subtitle_generator.get_transcript_text(clip_path)
                except Exception as e:
                    logger.warning(f"Failed to generate subtitles: {str(e)}")
            
            # Generate viral content
            content = None
            if generate_content:
                logger.info(f"Generating viral content for clip {i}...")
                content = self.content_generator.generate_viral_content(
                    video_title=video_info.get('title', ''),
                    video_description=video_info.get('description', ''),
                    clip_context=transcript[:200] if transcript else "",
                    duration=end_time - start_time
                )
            
            # Save metadata
            metadata = {
                'clip_number': i,
                'original_video': video_info.get('title', 'Unknown'),
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'clip_path': clip_path,
                'thumbnail_path': thumbnail_path,
                'subtitle_path': subtitle_path,
                'transcript': transcript,
                'viral_content': content,
                'created_at': timestamp
            }
            
            # Save metadata to JSON
            metadata_path = str(Config.METADATA_DIR / f"{clip_name}_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            metadata['metadata_path'] = metadata_path
            results.append(metadata)
            
            logger.info(f"Clip {i} completed successfully")
        
        logger.info(f"Generated {len(results)} viral clips successfully!")
        
        return results
    
    def _create_time_based_scenes(self, duration: float) -> List[tuple]:
        """Create simple time-based scenes as fallback.
        
        Args:
            duration: Video duration in seconds
            
        Returns:
            List of (start, end) tuples
        """
        scenes = []
        scene_length = 60  # 60 second scenes
        
        for start in range(0, int(duration), scene_length):
            end = min(start + scene_length, duration)
            scenes.append((start, end))
        
        return scenes
    
    def _create_fallback_moments(
        self, 
        duration: float, 
        num_clips: int
    ) -> List[tuple]:
        """Create fallback moments when scene detection fails.
        
        Args:
            duration: Video duration in seconds
            num_clips: Number of clips to create
            
        Returns:
            List of (start, end) tuples
        """
        moments = []
        clip_duration = min(Config.DEFAULT_CLIP_DURATION, duration / num_clips)
        
        # Divide video into equal parts
        segment_length = duration / num_clips
        
        for i in range(num_clips):
            start = i * segment_length
            end = start + clip_duration
            
            if end <= duration:
                moments.append((start, end))
        
        return moments
