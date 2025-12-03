import ffmpeg
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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
    
    @staticmethod
    def export_viral_clip(
        video_path: str,
        output_dir: str,
        start_time: float,
        end_time: float,
        clip_name: str = "viral_clip",
        target_platform: str = "shorts",  # shorts, tiktok, reels
        aspect_ratio: str = "9:16"
    ) -> str:
        """
        Export viral clip optimized for social media platforms
        - Trims video to specified duration
        - Resizes/crops to target aspect ratio (9:16 for vertical)
        - Optimizes quality and file size
        
        Returns: path to exported clip
        """
        try:
            # Create output directory
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in clip_name if c.isalnum() or c in (' ', '-', '_')).strip()
            output_filename = f"{safe_name}_{timestamp}.mp4"
            output_path = output_dir_path / output_filename
            
            duration = end_time - start_time
            
            # Get video info for aspect ratio calculations
            video_info = VideoProcessor.get_video_info(video_path)
            input_width = video_info['width']
            input_height = video_info['height']
            input_aspect = input_width / input_height
            
            # Calculate target dimensions based on platform
            if target_platform in ['shorts', 'tiktok', 'reels'] and aspect_ratio == "9:16":
                # Vertical format for Shorts/TikTok/Reels
                target_width = 1080
                target_height = 1920
            elif aspect_ratio == "16:9":
                # Horizontal format
                target_width = 1920
                target_height = 1080
            elif aspect_ratio == "1:1":
                # Square format (Instagram feed)
                target_width = 1080
                target_height = 1080
            else:
                # Keep original dimensions
                target_width = input_width
                target_height = input_height
            
            target_aspect = target_width / target_height
            
            # Input stream with trim
            stream = ffmpeg.input(video_path, ss=start_time, t=duration)
            
            # Apply scaling and cropping for aspect ratio conversion
            if abs(input_aspect - target_aspect) > 0.01:  # Need aspect ratio conversion
                if input_aspect > target_aspect:
                    # Input is wider - crop sides
                    scale_height = target_height
                    scale_width = int(input_aspect * scale_height)
                    crop_x = (scale_width - target_width) // 2
                    
                    stream = ffmpeg.filter(stream, 'scale', scale_width, scale_height)
                    stream = ffmpeg.filter(stream, 'crop', target_width, target_height, crop_x, 0)
                else:
                    # Input is taller - crop top/bottom
                    scale_width = target_width
                    scale_height = int(scale_width / input_aspect)
                    crop_y = (scale_height - target_height) // 2
                    
                    stream = ffmpeg.filter(stream, 'scale', scale_width, scale_height)
                    stream = ffmpeg.filter(stream, 'crop', target_width, target_height, 0, crop_y)
            else:
                # Just scale to target dimensions
                stream = ffmpeg.filter(stream, 'scale', target_width, target_height)
            
            # Output with optimized settings for social media
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec='libx264',
                acodec='aac',
                preset='medium',
                crf=23,  # Good quality for social media
                **{
                    'b:v': '3M',  # 3 Mbps video bitrate
                    'b:a': '128k',  # 128 kbps audio bitrate
                    'movflags': '+faststart',  # Enable fast start for web
                    'pix_fmt': 'yuv420p'  # Compatibility
                }
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Failed to export viral clip: {str(e)}")
    
    @staticmethod
    def generate_clip_subtitle_file(
        subtitles: List[Dict],
        clip_start_time: float,
        clip_end_time: float,
        output_path: str,
        style: Optional[Dict] = None
    ) -> str:
        """
        Generate ASS subtitle file for a clip with custom styling.
        Adjusts subtitle timing relative to clip start.
        
        Args:
            subtitles: List of subtitle segments with start_time, end_time, text
            clip_start_time: Start time of the clip in the original video
            clip_end_time: End time of the clip in the original video
            output_path: Path to save the ASS file
            style: Custom style settings
        
        Returns: Path to the generated ASS file
        """
        # Default viral-style subtitle settings
        default_style = {
            'font_name': 'Arial',
            'font_size': 48,
            'primary_color': '&H00FFFFFF',  # White
            'outline_color': '&H00000000',  # Black outline
            'back_color': '&H80000000',     # Semi-transparent black
            'bold': True,
            'outline': 3,
            'shadow': 2,
            'alignment': 2,  # Bottom center
            'margin_v': 60,  # Vertical margin from bottom
            'margin_l': 40,
            'margin_r': 40,
        }
        
        # Merge with custom style
        if style:
            default_style.update(style)
        s = default_style
        
        # ASS header with style
        ass_content = f"""[Script Info]
Title: Viral Clip Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{s['font_name']},{s['font_size']},{s['primary_color']},&H000000FF,{s['outline_color']},{s['back_color']},{1 if s['bold'] else 0},0,0,0,100,100,0,0,1,{s['outline']},{s['shadow']},{s['alignment']},{s['margin_l']},{s['margin_r']},{s['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Filter and adjust subtitles for clip timing
        for sub in subtitles:
            sub_start = sub['start_time']
            sub_end = sub['end_time']
            
            # Check if subtitle overlaps with clip
            if sub_end <= clip_start_time or sub_start >= clip_end_time:
                continue
            
            # Adjust timing relative to clip start
            adjusted_start = max(0, sub_start - clip_start_time)
            adjusted_end = min(clip_end_time - clip_start_time, sub_end - clip_start_time)
            
            # Format time as H:MM:SS.cc
            def format_ass_time(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                sec = int(seconds % 60)
                cs = int((seconds % 1) * 100)
                return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"
            
            start_str = format_ass_time(adjusted_start)
            end_str = format_ass_time(adjusted_end)
            
            # Clean text and add line breaks for long text
            text = sub['text'].strip()
            # Add soft line break for long lines
            words = text.split()
            if len(words) > 6:
                mid = len(words) // 2
                text = ' '.join(words[:mid]) + '\\N' + ' '.join(words[mid:])
            
            ass_content += f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}\n"
        
        # Write ASS file
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        return output_path
    
    @staticmethod
    def export_viral_clip_with_subtitles(
        video_path: str,
        output_dir: str,
        start_time: float,
        end_time: float,
        subtitles: List[Dict],
        clip_name: str = "viral_clip",
        target_platform: str = "shorts",
        aspect_ratio: str = "9:16",
        subtitle_style: Optional[Dict] = None
    ) -> str:
        """
        Export viral clip with burned-in subtitles optimized for social media.
        
        Args:
            video_path: Source video path
            output_dir: Output directory
            start_time: Clip start time
            end_time: Clip end time
            subtitles: List of subtitle segments
            clip_name: Name for the output file
            target_platform: Target platform (shorts, tiktok, reels)
            aspect_ratio: Target aspect ratio
            subtitle_style: Custom subtitle styling
        
        Returns: Path to exported clip with subtitles
        """
        try:
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in clip_name if c.isalnum() or c in (' ', '-', '_')).strip()
            output_filename = f"{safe_name}_{timestamp}.mp4"
            output_path = output_dir_path / output_filename
            
            # Generate ASS subtitle file
            ass_path = output_dir_path / f"{safe_name}_{timestamp}.ass"
            VideoProcessor.generate_clip_subtitle_file(
                subtitles=subtitles,
                clip_start_time=start_time,
                clip_end_time=end_time,
                output_path=str(ass_path),
                style=subtitle_style
            )
            
            duration = end_time - start_time
            
            # Get video info
            video_info = VideoProcessor.get_video_info(video_path)
            input_width = video_info['width']
            input_height = video_info['height']
            input_aspect = input_width / input_height
            
            # Calculate target dimensions
            if target_platform in ['shorts', 'tiktok', 'reels'] and aspect_ratio == "9:16":
                target_width = 1080
                target_height = 1920
            elif aspect_ratio == "16:9":
                target_width = 1920
                target_height = 1080
            elif aspect_ratio == "1:1":
                target_width = 1080
                target_height = 1080
            else:
                target_width = input_width
                target_height = input_height
            
            target_aspect = target_width / target_height
            
            # Build filter chain
            filters = []
            
            # Scaling and cropping
            if abs(input_aspect - target_aspect) > 0.01:
                if input_aspect > target_aspect:
                    scale_height = target_height
                    scale_width = int(input_aspect * scale_height)
                    crop_x = (scale_width - target_width) // 2
                    filters.append(f"scale={scale_width}:{scale_height}")
                    filters.append(f"crop={target_width}:{target_height}:{crop_x}:0")
                else:
                    scale_width = target_width
                    scale_height = int(scale_width / input_aspect)
                    crop_y = (scale_height - target_height) // 2
                    filters.append(f"scale={scale_width}:{scale_height}")
                    filters.append(f"crop={target_width}:{target_height}:0:{crop_y}")
            else:
                filters.append(f"scale={target_width}:{target_height}")
            
            # Add subtitle filter - escape path for Windows
            ass_path_escaped = str(ass_path).replace('\\', '/').replace(':', r'\:')
            filters.append(f"ass='{ass_path_escaped}'")
            
            filter_chain = ','.join(filters)
            
            # Build ffmpeg command manually for better control
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-t', str(duration),
                '-i', video_path,
                '-vf', filter_chain,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p',
                str(output_path)
            ]
            
            # Run ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # If ASS subtitle fails, try without subtitles
                print(f"[WARN] Subtitle burn failed, exporting without subtitles: {result.stderr[:200]}")
                return VideoProcessor.export_viral_clip(
                    video_path, output_dir, start_time, end_time,
                    clip_name, target_platform, aspect_ratio
                )
            
            # Clean up ASS file
            try:
                ass_path.unlink()
            except:
                pass
            
            return str(output_path)
            
        except Exception as e:
            print(f"[ERROR] Export with subtitles failed: {e}, falling back to no subtitles")
            return VideoProcessor.export_viral_clip(
                video_path, output_dir, start_time, end_time,
                clip_name, target_platform, aspect_ratio
            )
    
    @staticmethod
    def get_default_subtitle_styles():
        """
        Returns predefined subtitle styles for different aesthetics
        """
        return {
            'viral_white': {
                'font_name': 'Arial',
                'font_size': 52,
                'primary_color': '&H00FFFFFF',  # White
                'outline_color': '&H00000000',  # Black
                'back_color': '&H80000000',
                'bold': True,
                'outline': 3,
                'shadow': 2,
                'alignment': 2,
                'margin_v': 80,
            },
            'viral_yellow': {
                'font_name': 'Impact',
                'font_size': 56,
                'primary_color': '&H0000FFFF',  # Yellow
                'outline_color': '&H00000000',
                'back_color': '&H00000000',
                'bold': True,
                'outline': 4,
                'shadow': 0,
                'alignment': 2,
                'margin_v': 100,
            },
            'mrbeast': {
                'font_name': 'Impact',
                'font_size': 64,
                'primary_color': '&H00FFFFFF',  # White
                'outline_color': '&H00000000',
                'back_color': '&H00000000',
                'bold': True,
                'outline': 5,
                'shadow': 3,
                'alignment': 2,
                'margin_v': 120,
            },
            'minimal': {
                'font_name': 'Helvetica',
                'font_size': 42,
                'primary_color': '&H00FFFFFF',
                'outline_color': '&H40000000',
                'back_color': '&H00000000',
                'bold': False,
                'outline': 2,
                'shadow': 0,
                'alignment': 2,
                'margin_v': 60,
            },
            'karaoke_highlight': {
                'font_name': 'Arial Black',
                'font_size': 48,
                'primary_color': '&H0000FF00',  # Green highlight
                'outline_color': '&H00000000',
                'back_color': '&H80000000',
                'bold': True,
                'outline': 3,
                'shadow': 2,
                'alignment': 2,
                'margin_v': 80,
            },
        }
