from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# Get base directory (backend folder)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Database - use absolute path
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'viralclip.db'}"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App Config - use absolute paths
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    TEMP_DIR: str = str(BASE_DIR / "temp")
    MAX_UPLOAD_SIZE: int = 2000000000  # 2GB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure directories exist (but NOT database - use migrations!)
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.TEMP_DIR).mkdir(exist_ok=True)

# NOTE: Database tables should be created via Alembic migrations
# Run: python migrate.py migrate
