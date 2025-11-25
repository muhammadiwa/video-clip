from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from celery.result import AsyncResult
from app.core.celery_app import celery_app

router = APIRouter()

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.get("/status/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    """
    Get status of a background job
    """
    try:
        task_result = AsyncResult(job_id, app=celery_app)
        
        response = {
            "job_id": job_id,
            "status": task_result.state,
        }
        
        if task_result.state == 'PENDING':
            response["progress"] = {
                "current": 0,
                "total": 100,
                "status": "Job is waiting to be processed..."
            }
        elif task_result.state == 'PROGRESS':
            response["progress"] = task_result.info
        elif task_result.state == 'SUCCESS':
            response["result"] = task_result.result
            response["progress"] = {
                "current": 100,
                "total": 100,
                "status": "Job completed successfully"
            }
        elif task_result.state == 'FAILURE':
            response["error"] = str(task_result.info.get('error', 'Unknown error'))
            response["progress"] = {
                "current": 0,
                "total": 100,
                "status": "Job failed"
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.post("/cancel/{job_id}")
def cancel_job(job_id: str):
    """
    Cancel a background job
    """
    try:
        task_result = AsyncResult(job_id, app=celery_app)
        task_result.revoke(terminate=True)
        
        return {
            "job_id": job_id,
            "status": "cancelled",
            "message": "Job cancellation requested"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

@router.get("/active")
def get_active_jobs():
    """
    Get list of active jobs
    """
    try:
        # Get active tasks from Celery
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return {"active_jobs": []}
        
        # Flatten active tasks from all workers
        all_active = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                all_active.append({
                    "job_id": task["id"],
                    "name": task["name"],
                    "worker": worker,
                    "time_start": task.get("time_start"),
                })
        
        return {"active_jobs": all_active}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active jobs: {str(e)}")

@router.get("/scheduled")
def get_scheduled_jobs():
    """
    Get list of scheduled jobs
    """
    try:
        inspect = celery_app.control.inspect()
        scheduled_tasks = inspect.scheduled()
        
        if not scheduled_tasks:
            return {"scheduled_jobs": []}
        
        # Flatten scheduled tasks from all workers
        all_scheduled = []
        for worker, tasks in scheduled_tasks.items():
            for task in tasks:
                all_scheduled.append({
                    "job_id": task["request"]["id"],
                    "name": task["request"]["name"],
                    "worker": worker,
                    "eta": task.get("eta"),
                })
        
        return {"scheduled_jobs": all_scheduled}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduled jobs: {str(e)}")

@router.get("/stats")
def get_celery_stats():
    """
    Get Celery worker statistics
    """
    try:
        inspect = celery_app.control.inspect()
        
        stats = inspect.stats()
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        
        return {
            "workers": list(stats.keys()) if stats else [],
            "stats": stats,
            "active_count": sum(len(tasks) for tasks in active.values()) if active else 0,
            "scheduled_count": sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0,
            "reserved_count": sum(len(tasks) for tasks in reserved.values()) if reserved else 0,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Celery stats: {str(e)}")
