"""Configuration management for the application."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent.parent
    OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
    CLIP_DIR = BASE_DIR / os.getenv("CLIP_DIR", "output/clips")
    THUMBNAIL_DIR = BASE_DIR / os.getenv("THUMBNAIL_DIR", "output/thumbnails")
    METADATA_DIR = BASE_DIR / os.getenv("METADATA_DIR", "output/metadata")
    
    # Video processing settings
    MIN_CLIP_DURATION = int(os.getenv("MIN_CLIP_DURATION", "30"))
    MAX_CLIP_DURATION = int(os.getenv("MAX_CLIP_DURATION", "360"))
    DEFAULT_CLIP_DURATION = int(os.getenv("DEFAULT_CLIP_DURATION", "60"))
    TARGET_RESOLUTION = os.getenv("TARGET_RESOLUTION", "1080x1920")
    
    # Scene detection settings
    SCENE_THRESHOLD = float(os.getenv("SCENE_THRESHOLD", "27.0"))
    MIN_SCENE_LENGTH = float(os.getenv("MIN_SCENE_LENGTH", "3.0"))
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all output directories exist."""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CLIP_DIR.mkdir(parents=True, exist_ok=True)
        cls.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
        cls.METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_target_resolution(cls):
        """Get target resolution as tuple (width, height)."""
        width, height = cls.TARGET_RESOLUTION.split('x')
        return int(width), int(height)
