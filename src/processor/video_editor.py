"""Video editing and processing functionality."""

import os
from pathlib import Path
from typing import Tuple, Optional
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import resize, crop
from src.utils.logger import logger
from src.utils.config import Config


class VideoEditor:
    """Edit and process videos."""
    
    def __init__(self):
        """Initialize video editor."""
        self.target_width, self.target_height = Config.get_target_resolution()
    
    def extract_clip(
        self, 
        video_path: str, 
        start_time: float, 
        end_time: float,
        output_path: str,
        convert_to_shorts: bool = True
    ) -> str:
        """Extract a clip from a video.
        
        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Path to save the clip
            convert_to_shorts: Convert to YouTube Shorts format (9:16)
            
        Returns:
            Path to the extracted clip
        """
        logger.info(f"Extracting clip from {start_time:.2f}s to {end_time:.2f}s")
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Extract subclip
            clip = video.subclip(start_time, end_time)
            
            # Convert to YouTube Shorts format if requested
            if convert_to_shorts:
                clip = self._convert_to_shorts_format(clip)
            
            # Write output
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=30
            )
            
            # Clean up
            clip.close()
            video.close()
            
            logger.info(f"Clip saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting clip: {str(e)}")
            raise
    
    def _convert_to_shorts_format(self, clip: VideoFileClip) -> VideoFileClip:
        """Convert video to YouTube Shorts format (9:16 aspect ratio, 1080x1920).
        
        Args:
            clip: Video clip to convert
            
        Returns:
            Converted video clip
        """
        logger.info("Converting to YouTube Shorts format (9:16)")
        
        # Get current dimensions
        current_width, current_height = clip.size
        current_aspect = current_width / current_height
        target_aspect = self.target_width / self.target_height  # 9:16 = 0.5625
        
        # If video is already in portrait mode or close to it
        if current_aspect <= target_aspect * 1.1:
            # Just resize to target resolution
            clip = clip.resize(height=self.target_height)
            
            # If width is still too large, crop it
            if clip.size[0] > self.target_width:
                x_center = clip.size[0] / 2
                x1 = int(x_center - self.target_width / 2)
                clip = crop(clip, x1=x1, width=self.target_width)
        else:
            # Video is in landscape mode, need to crop and resize
            # Crop to 9:16 aspect ratio from the center
            new_width = int(current_height * target_aspect)
            x_center = current_width / 2
            x1 = int(x_center - new_width / 2)
            
            clip = crop(clip, x1=x1, width=new_width, y1=0, height=current_height)
            
            # Resize to target resolution
            clip = clip.resize(height=self.target_height)
        
        return clip
    
    def extract_thumbnail(
        self, 
        video_path: str, 
        time: float = None,
        output_path: str = None
    ) -> str:
        """Extract a thumbnail from a video.
        
        Args:
            video_path: Path to video file
            time: Time in seconds to extract frame (default: middle of video)
            output_path: Path to save thumbnail
            
        Returns:
            Path to saved thumbnail
        """
        try:
            video = VideoFileClip(video_path)
            
            # Use middle of video if time not specified
            if time is None:
                time = video.duration / 2
            
            # Generate output path if not provided
            if output_path is None:
                video_name = Path(video_path).stem
                output_path = str(Config.THUMBNAIL_DIR / f"{video_name}_thumb.jpg")
            
            # Extract frame
            frame = video.get_frame(time)
            
            # Save as image
            from PIL import Image
            img = Image.fromarray(frame)
            img.save(output_path, quality=95)
            
            video.close()
            
            logger.info(f"Thumbnail saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting thumbnail: {str(e)}")
            raise
    
    def get_video_info(self, video_path: str) -> dict:
        """Get information about a video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            video = VideoFileClip(video_path)
            
            info = {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'width': video.size[0],
                'height': video.size[1],
                'aspect_ratio': video.size[0] / video.size[1],
            }
            
            video.close()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise
