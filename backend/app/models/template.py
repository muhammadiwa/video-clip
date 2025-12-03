from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class ProcessingTemplate(Base):
    __tablename__ = "processing_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    
    # Processing settings
    top_n = Column(Integer, default=5)
    target_platform = Column(String, default="shorts")
    aspect_ratio = Column(String, default="9:16")
    burn_subtitles = Column(Boolean, default=True)
    subtitle_style = Column(String, default="viral_white")
    min_duration = Column(Float, default=30.0)
    max_duration = Column(Float, default=60.0)
    
    # Additional settings (JSON for flexibility)
    settings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
