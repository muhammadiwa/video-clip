import yt_dlp
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

class YouTubeDownloader:
    """YouTube video downloader using yt-dlp"""
    
    @staticmethod
    def download_video(
        url: str,
        output_dir: str,
        quality: str = 'best'
    ) -> Dict:
        """
        Download YouTube video
        Returns: dict with file_path, title, duration, thumbnail
        """
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_template = str(output_path / f"yt_{timestamp}_%(title)s.%(ext)s")
            
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'writethumbnail': True,
                'writesubtitles': False,
                'writeautomaticsub': False,
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get downloaded file path
                filename = ydl.prepare_filename(info)
                
                result = {
                    'file_path': filename,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'fps': info.get('fps', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                }
                
                return result
                
        except Exception as e:
            raise Exception(f"Failed to download YouTube video: {str(e)}")
    
    @staticmethod
    def get_video_info(url: str) -> Dict:
        """
        Get YouTube video info without downloading
        Returns: video metadata
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'fps': info.get('fps', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                }
                
        except Exception as e:
            raise Exception(f"Failed to get YouTube video info: {str(e)}")
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if URL is a valid YouTube URL
        """
        youtube_domains = [
            'youtube.com',
            'youtu.be',
            'www.youtube.com',
            'm.youtube.com'
        ]
        return any(domain in url for domain in youtube_domains)
