"""Subtitle generation using speech recognition."""

import os
from pathlib import Path
from typing import Optional
import whisper
from moviepy.editor import VideoFileClip
from src.utils.logger import logger


class SubtitleGenerator:
    """Generate subtitles from video audio using Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """Initialize subtitle generator.
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"Subtitle generator initialized with model: {model_name}")
    
    def _load_model(self):
        """Load Whisper model lazily."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
    
    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """Extract audio from video.
        
        Args:
            video_path: Path to video file
            output_path: Path to save audio file (default: temp file)
            
        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            output_path = f"/tmp/{Path(video_path).stem}_audio.wav"
        
        logger.info(f"Extracting audio from video: {video_path}")
        
        try:
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(output_path, verbose=False, logger=None)
            video.close()
            
            logger.info(f"Audio extracted to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    def generate_subtitles(
        self, 
        video_path: str,
        output_path: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """Generate subtitles for a video.
        
        Args:
            video_path: Path to video file
            output_path: Path to save subtitle file (SRT format)
            language: Language code for transcription
            
        Returns:
            Path to subtitle file
        """
        logger.info(f"Generating subtitles for: {video_path}")
        
        # Load model if not loaded
        self._load_model()
        
        # Extract audio
        audio_path = self.extract_audio(video_path)
        
        try:
            # Transcribe audio
            logger.info("Transcribing audio...")
            result = self.model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )
            
            # Generate output path if not provided
            if output_path is None:
                output_path = str(Path(video_path).with_suffix('.srt'))
            
            # Write SRT file
            self._write_srt(result['segments'], output_path)
            
            # Clean up temp audio file
            if os.path.exists(audio_path) and audio_path.startswith('/tmp/'):
                os.remove(audio_path)
            
            logger.info(f"Subtitles saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating subtitles: {str(e)}")
            raise
    
    def _write_srt(self, segments: list, output_path: str):
        """Write segments to SRT file format.
        
        Args:
            segments: List of transcript segments
            output_path: Path to save SRT file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, start=1):
                # Write subtitle index
                f.write(f"{i}\n")
                
                # Write timestamp
                start = self._format_timestamp(segment['start'])
                end = self._format_timestamp(segment['end'])
                f.write(f"{start} --> {end}\n")
                
                # Write text
                f.write(f"{segment['text'].strip()}\n\n")
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def get_transcript_text(self, video_path: str, language: str = "en") -> str:
        """Get transcript text without timestamps.
        
        Args:
            video_path: Path to video file
            language: Language code for transcription
            
        Returns:
            Full transcript text
        """
        logger.info(f"Getting transcript for: {video_path}")
        
        # Load model if not loaded
        self._load_model()
        
        # Extract audio
        audio_path = self.extract_audio(video_path)
        
        try:
            # Transcribe audio
            result = self.model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )
            
            # Clean up temp audio file
            if os.path.exists(audio_path) and audio_path.startswith('/tmp/'):
                os.remove(audio_path)
            
            return result['text'].strip()
            
        except Exception as e:
            logger.error(f"Error getting transcript: {str(e)}")
            raise
