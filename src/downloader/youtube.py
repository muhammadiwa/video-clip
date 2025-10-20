"""YouTube video downloader using yt-dlp."""

import os
from pathlib import Path
from typing import Optional, Dict
import yt_dlp
from src.utils.logger import logger


class YouTubeDownloader:
    """Download videos from YouTube."""
    
    def __init__(self, output_dir: str = "/tmp"):
        """Initialize YouTube downloader.
        
        Args:
            output_dir: Directory to save downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self, url: str, output_filename: Optional[str] = None) -> Dict[str, str]:
        """Download a YouTube video.
        
        Args:
            url: YouTube video URL
            output_filename: Optional custom filename (without extension)
            
        Returns:
            Dictionary with video info and file path
        """
        logger.info(f"Downloading video from: {url}")
        
        if output_filename:
            output_template = str(self.output_dir / f"{output_filename}.%(ext)s")
        else:
            output_template = str(self.output_dir / "%(id)s.%(ext)s")
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'merge_output_format': 'mp4',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get the actual filename
                if output_filename:
                    video_path = str(self.output_dir / f"{output_filename}.mp4")
                else:
                    video_path = str(self.output_dir / f"{info['id']}.mp4")
                
                logger.info(f"Video downloaded successfully: {video_path}")
                
                return {
                    'path': video_path,
                    'title': info.get('title', 'Unknown'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                }
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
    
    def get_video_info(self, url: str) -> Dict:
        """Get video information without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video information
        """
        logger.info(f"Fetching video info from: {url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                }
        except Exception as e:
            logger.error(f"Error fetching video info: {str(e)}")
            raise
