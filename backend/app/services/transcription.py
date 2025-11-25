import whisper
import os
from typing import Dict, List, Optional
from pathlib import Path
import json

class TranscriptionService:
    """OpenAI Whisper transcription service"""
    
    # Model size options: tiny, base, small, medium, large
    DEFAULT_MODEL = "base"
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.model = None
    
    def load_model(self):
        """Load Whisper model"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            print("Model loaded successfully")
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio file using Whisper
        Args:
            audio_path: path to audio file
            language: ISO 639-1 language code (e.g., 'en', 'id', 'es')
            task: 'transcribe' or 'translate' (translate to English)
        Returns: transcription with segments and text
        """
        try:
            self.load_model()
            
            options = {
                "task": task,
                "verbose": False,
            }
            
            if language:
                options["language"] = language
            
            # Transcribe
            result = self.model.transcribe(audio_path, **options)
            
            # Process segments
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "id": segment["id"],
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": segment.get("avg_logprob", 0),
                })
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": segments,
                "duration": segments[-1]["end"] if segments else 0,
            }
            
        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    def transcribe_video(
        self,
        video_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe video file (extracts audio first if needed)
        Returns: transcription with segments
        """
        try:
            # Whisper can handle video files directly
            return self.transcribe_audio(video_path, language, task)
            
        except Exception as e:
            raise Exception(f"Failed to transcribe video: {str(e)}")
    
    def save_transcription(
        self,
        transcription: Dict,
        output_path: str,
        format: str = "json"
    ):
        """
        Save transcription to file
        Formats: json, srt, vtt, txt
        """
        try:
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(transcription, f, indent=2, ensure_ascii=False)
                    
            elif format == "srt":
                srt_content = self._generate_srt(transcription["segments"])
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                    
            elif format == "vtt":
                vtt_content = self._generate_vtt(transcription["segments"])
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(vtt_content)
                    
            elif format == "txt":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(transcription["text"])
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            raise Exception(f"Failed to save transcription: {str(e)}")
    
    def _generate_srt(self, segments: List[Dict]) -> str:
        """Generate SRT subtitle format"""
        srt_lines = []
        
        for i, segment in enumerate(segments, start=1):
            start_time = self._format_timestamp_srt(segment["start"])
            end_time = self._format_timestamp_srt(segment["end"])
            text = segment["text"]
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def _generate_vtt(self, segments: List[Dict]) -> str:
        """Generate VTT subtitle format"""
        vtt_lines = ["WEBVTT", ""]
        
        for segment in segments:
            start_time = self._format_timestamp_vtt(segment["start"])
            end_time = self._format_timestamp_vtt(segment["end"])
            text = segment["text"]
            
            vtt_lines.append(f"{start_time} --> {end_time}")
            vtt_lines.append(text)
            vtt_lines.append("")
        
        return "\n".join(vtt_lines)
    
    def _format_timestamp_srt(self, seconds: float) -> str:
        """Format timestamp for SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _format_timestamp_vtt(self, seconds: float) -> str:
        """Format timestamp for VTT (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def extract_keywords(self, transcription: Dict, top_n: int = 10) -> List[str]:
        """
        Extract keywords from transcription
        Simple frequency-based extraction
        """
        try:
            text = transcription["text"].lower()
            
            # Remove common stop words (simplified)
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
                'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what',
                'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
                'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'
            }
            
            # Split into words
            words = text.split()
            words = [w.strip('.,!?;:') for w in words]
            words = [w for w in words if w and w not in stop_words and len(w) > 2]
            
            # Count frequency
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Return top N
            keywords = [word for word, freq in sorted_words[:top_n]]
            
            return keywords
            
        except Exception as e:
            raise Exception(f"Failed to extract keywords: {str(e)}")
