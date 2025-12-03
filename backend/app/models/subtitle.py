from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Subtitle(Base):
    __tablename__ = "subtitles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Support both video-level and clip-level subtitles
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    clip_id = Column(Integer, ForeignKey("clips.id"), nullable=True)
    
    # Subtitle content
    text = Column(String, nullable=False)
    start_time = Column(Float, nullable=False)  # seconds
    end_time = Column(Float, nullable=False)  # seconds
    
    # Styling
    style = Column(JSON, nullable=True)  # font, color, size, position, etc.
    
    # Language
    language = Column(String, default="en")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="subtitles")
    clip = relationship("Clip", back_populates="subtitles")
