from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="created")  # created, processing, ready, edited
    
    # Settings
    source_language = Column(String, default="en")
    target_platform = Column(String, default="shorts")  # shorts, reels, tiktok
    target_duration = Column(Integer, default=60)  # seconds
    aspect_ratio = Column(String, default="9:16")  # 9:16, 16:9, 1:1, 4:5
    
    # Metadata
    settings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    clips = relationship("Clip", back_populates="project", cascade="all, delete-orphan")
