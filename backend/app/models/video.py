from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Video info
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    
    # Video metadata
    duration = Column(Float, nullable=True)  # seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    codec = Column(String, nullable=True)
    bitrate = Column(Integer, nullable=True)  # bits per second
    
    # Source
    source_type = Column(String, default="upload")  # upload, youtube, vimeo
    source_url = Column(String, nullable=True)
    
    # Processing status
    status = Column(String, default="uploaded")  # uploaded, processing, processed, error
    processing_progress = Column(Integer, default=0)  # 0-100
    error_message = Column(String, nullable=True)
    
    # Extracted data
    audio_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    transcription_path = Column(String, nullable=True)
    has_transcription = Column(Boolean, default=False)
    transcript = Column(JSON, nullable=True)
    scenes = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="videos")
