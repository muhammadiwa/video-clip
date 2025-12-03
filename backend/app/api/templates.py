from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models.template import ProcessingTemplate

router = APIRouter()

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: Optional[bool] = False
    top_n: Optional[int] = 5
    target_platform: Optional[str] = "shorts"
    aspect_ratio: Optional[str] = "9:16"
    burn_subtitles: Optional[bool] = True
    subtitle_style: Optional[str] = "viral_white"
    min_duration: Optional[float] = 30.0
    max_duration: Optional[float] = 60.0
    settings: Optional[dict] = None

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    top_n: Optional[int] = None
    target_platform: Optional[str] = None
    aspect_ratio: Optional[str] = None
    burn_subtitles: Optional[bool] = None
    subtitle_style: Optional[str] = None
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    settings: Optional[dict] = None

class TemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_default: bool
    top_n: int
    target_platform: str
    aspect_ratio: str
    burn_subtitles: bool
    subtitle_style: str
    min_duration: float
    max_duration: float
    settings: Optional[dict]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new processing template"""
    if template.is_default:
        db.query(ProcessingTemplate).update({ProcessingTemplate.is_default: False})
    
    db_template = ProcessingTemplate(
        name=template.name,
        description=template.description,
        is_default=template.is_default,
        top_n=template.top_n,
        target_platform=template.target_platform,
        aspect_ratio=template.aspect_ratio,
        burn_subtitles=template.burn_subtitles,
        subtitle_style=template.subtitle_style,
        min_duration=template.min_duration,
        max_duration=template.max_duration,
        settings=template.settings
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/", response_model=List[TemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    """Get all processing templates"""
    return db.query(ProcessingTemplate).order_by(ProcessingTemplate.is_default.desc(), ProcessingTemplate.name).all()

@router.get("/default", response_model=Optional[TemplateResponse])
def get_default_template(db: Session = Depends(get_db)):
    """Get the default template"""
    return db.query(ProcessingTemplate).filter(ProcessingTemplate.is_default == True).first()

@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific template"""
    template = db.query(ProcessingTemplate).filter(ProcessingTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template: TemplateUpdate, db: Session = Depends(get_db)):
    """Update a template"""
    db_template = db.query(ProcessingTemplate).filter(ProcessingTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.is_default:
        db.query(ProcessingTemplate).update({ProcessingTemplate.is_default: False})
    
    update_data = template.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a template"""
    db_template = db.query(ProcessingTemplate).filter(ProcessingTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return {"message": "Template deleted successfully"}

@router.post("/{template_id}/set-default", response_model=TemplateResponse)
def set_default_template(template_id: int, db: Session = Depends(get_db)):
    """Set a template as default"""
    db_template = db.query(ProcessingTemplate).filter(ProcessingTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.query(ProcessingTemplate).update({ProcessingTemplate.is_default: False})
    db_template.is_default = True
    db.commit()
    db.refresh(db_template)
    return db_template
