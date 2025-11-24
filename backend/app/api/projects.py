from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.core.database import get_db
from app.models.project import Project

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: str = None
    source_language: str = "en"
    target_platform: str = "shorts"
    target_duration: int = 60
    aspect_ratio: str = "9:16"

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str = None
    status: str
    source_language: str
    target_platform: str
    target_duration: int
    aspect_ratio: str
    created_at: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(
        name=project.name,
        description=project.description,
        source_language=project.source_language,
        target_platform=project.target_platform,
        target_duration=project.target_duration,
        aspect_ratio=project.aspect_ratio,
        status="created"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
