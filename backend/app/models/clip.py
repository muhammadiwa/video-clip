from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Clip(Base):
    __tablename__ = "clips"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Clip info
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Timeline
    start_time = Column(Float, nullable=False)  # seconds
    end_time = Column(Float, nullable=False)  # seconds
    duration = Column(Float, nullable=False)  # seconds
    
    # AI Detection
    viral_score = Column(Float, default=0.0)  # 0-10
    category = Column(String, nullable=True)  # hook, story, punchline, cta
    keywords = Column(JSON, nullable=True)
    
    # Export settings
    aspect_ratio = Column(String, default="9:16")
    resolution = Column(String, default="1080p")
    fps = Column(Integer, default=30)
    
    # Editing data
    subtitle_style = Column(JSON, nullable=True)
    overlays = Column(JSON, nullable=True)
    audio_settings = Column(JSON, nullable=True)
    
    # Status
    status = Column(String, default="detected")  # detected, edited, exported
    exported = Column(Boolean, default=False)
    export_path = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="clips")
    subtitles = relationship("Subtitle", back_populates="clip", cascade="all, delete-orphan")
