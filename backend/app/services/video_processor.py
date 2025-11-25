import ffmpeg
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

class VideoProcessor:
    """FFmpeg video processing service"""
    
    @staticmethod
    def get_video_info(file_path: str) -> Dict:
        """
        Extract video metadata using FFmpeg
        Returns: duration, width, height, codec, bitrate, fps
        """
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
                None
            )
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'codec': video_stream.get('codec_name', 'unknown'),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'bitrate': int(probe['format'].get('bit_rate', 0)),
                'size': int(probe['format'].get('size', 0)),
                'format': probe['format'].get('format_name', 'unknown'),
                'has_audio': audio_stream is not None,
            }
            
            if audio_stream:
                info['audio_codec'] = audio_stream.get('codec_name', 'unknown')
                info['audio_sample_rate'] = int(audio_stream.get('sample_rate', 0))
            
            return info
            
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    @staticmethod
    def extract_audio(video_path: str, output_dir: str) -> str:
        """
        Extract audio from video file
        Returns: path to extracted audio file
        """
        try:
            video_path_obj = Path(video_path)
            output_filename = f"{video_path_obj.stem}_audio.wav"
            output_path = Path(output_dir) / output_filename
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Extract audio
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='pcm_s16le',  # WAV format
                ac=1,  # Mono
                ar='16000'  # 16kHz sample rate (optimal for Whisper)
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Failed to extract audio: {str(e)}")
    
    @staticmethod
    def generate_thumbnail(video_path: str, output_dir: str, timestamp: float = 1.0) -> str:
        """
        Generate thumbnail from video at specific timestamp
        Returns: path to thumbnail image
        """
        try:
            video_path_obj = Path(video_path)
            output_filename = f"{video_path_obj.stem}_thumb.jpg"
            output_path = Path(output_dir) / output_filename
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate thumbnail
            stream = ffmpeg.input(video_path, ss=timestamp)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vframes=1,
                format='image2',
                vcodec='mjpeg',
                **{'q:v': 2}  # Quality (lower is better, 2-31)
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Failed to generate thumbnail: {str(e)}")
    
    @staticmethod
    def trim_video(
        video_path: str,
        output_dir: str,
        start_time: float,
        end_time: float
    ) -> str:
        """
        Trim video to specific time range
        Returns: path to trimmed video
        """
        try:
            video_path_obj = Path(video_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{video_path_obj.stem}_trim_{timestamp}.mp4"
            output_path = Path(output_dir) / output_filename
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            duration = end_time - start_time
            
            # Trim video
            stream = ffmpeg.input(video_path, ss=start_time, t=duration)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec='libx264',
                acodec='aac',
                preset='medium',
                crf=23
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Failed to trim video: {str(e)}")
    
    @staticmethod
    def compress_video(
        video_path: str,
        output_dir: str,
        target_size_mb: Optional[int] = None,
        crf: int = 28
    ) -> str:
        """
        Compress video file
        Returns: path to compressed video
        """
        try:
            video_path_obj = Path(video_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{video_path_obj.stem}_compressed_{timestamp}.mp4"
            output_path = Path(output_dir) / output_filename
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Compress video
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec='libx264',
                acodec='aac',
                crf=crf,  # Quality (lower is better, 0-51)
                preset='medium'
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Failed to compress video: {str(e)}")
    
    @staticmethod
    def convert_format(
        video_path: str,
        output_dir: str,
        output_format: str = 'mp4'
    ) -> str:
        """
        Convert video to different format
        Returns: path to converted video
        """
        try:
            video_path_obj = Path(video_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{video_path_obj.stem}_{timestamp}.{output_format}"
            output_path = Path(output_dir) / output_filename
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert format
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec='libx264',
                acodec='aac'
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Failed to convert format: {str(e)}")
