"""
Webhook Notifications API
Allows external services to receive notifications about processing events
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import httpx
import json

from app.core.database import get_db

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# In-memory storage for webhooks (in production, use database)
webhooks_store: dict = {}


class WebhookCreate(BaseModel):
    url: str
    events: List[str]  # ["clip.created", "clip.exported", "processing.complete", "processing.failed"]
    secret: Optional[str] = None
    active: Optional[bool] = True


class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    active: bool
    created_at: str
    last_triggered: Optional[str] = None


VALID_EVENTS = [
    "clip.created",
    "clip.exported", 
    "clip.deleted",
    "processing.started",
    "processing.complete",
    "processing.failed",
    "video.uploaded",
    "video.deleted",
]


@router.get("")
def list_webhooks():
    """List all registered webhooks"""
    return {
        "webhooks": list(webhooks_store.values()),
        "total": len(webhooks_store)
    }


@router.post("")
def create_webhook(webhook: WebhookCreate):
    """Register a new webhook endpoint"""
    # Validate events
    invalid_events = [e for e in webhook.events if e not in VALID_EVENTS]
    if invalid_events:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid events: {invalid_events}. Valid events: {VALID_EVENTS}"
        )
    
    # Generate ID
    webhook_id = f"wh_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(webhooks_store)}"
    
    webhook_data = {
        "id": webhook_id,
        "url": webhook.url,
        "events": webhook.events,
        "secret": webhook.secret,
        "active": webhook.active,
        "created_at": datetime.now().isoformat(),
        "last_triggered": None
    }
    
    webhooks_store[webhook_id] = webhook_data
    
    # Return without secret
    return {
        "id": webhook_id,
        "url": webhook.url,
        "events": webhook.events,
        "active": webhook.active,
        "created_at": webhook_data["created_at"],
        "message": "Webhook registered successfully"
    }


@router.get("/{webhook_id}")
def get_webhook(webhook_id: str):
    """Get webhook details"""
    if webhook_id not in webhooks_store:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook = webhooks_store[webhook_id].copy()
    webhook.pop("secret", None)  # Don't expose secret
    return webhook


@router.put("/{webhook_id}")
def update_webhook(webhook_id: str, update: WebhookUpdate):
    """Update webhook configuration"""
    if webhook_id not in webhooks_store:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook = webhooks_store[webhook_id]
    
    if update.url is not None:
        webhook["url"] = update.url
    if update.events is not None:
        invalid_events = [e for e in update.events if e not in VALID_EVENTS]
        if invalid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid events: {invalid_events}"
            )
        webhook["events"] = update.events
    if update.secret is not None:
        webhook["secret"] = update.secret
    if update.active is not None:
        webhook["active"] = update.active
    
    result = webhook.copy()
    result.pop("secret", None)
    return result


@router.delete("/{webhook_id}")
def delete_webhook(webhook_id: str):
    """Delete a webhook"""
    if webhook_id not in webhooks_store:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks_store[webhook_id]
    return {"message": "Webhook deleted successfully"}


@router.post("/{webhook_id}/test")
async def test_webhook(webhook_id: str):
    """Send a test event to the webhook"""
    if webhook_id not in webhooks_store:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook = webhooks_store[webhook_id]
    
    test_payload = {
        "event": "test",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "message": "This is a test webhook event",
            "webhook_id": webhook_id
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            if webhook.get("secret"):
                headers["X-Webhook-Secret"] = webhook["secret"]
            
            response = await client.post(
                webhook["url"],
                json=test_payload,
                headers=headers,
                timeout=10.0
            )
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "message": "Test event sent successfully" if response.status_code < 400 else "Webhook endpoint returned error"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send test event"
        }


@router.get("/events/list")
def list_events():
    """List all available webhook events"""
    return {
        "events": VALID_EVENTS,
        "descriptions": {
            "clip.created": "Fired when a new clip is detected",
            "clip.exported": "Fired when a clip is exported successfully",
            "clip.deleted": "Fired when a clip is deleted",
            "processing.started": "Fired when video processing begins",
            "processing.complete": "Fired when video processing completes",
            "processing.failed": "Fired when video processing fails",
            "video.uploaded": "Fired when a new video is uploaded",
            "video.deleted": "Fired when a video is deleted",
        }
    }


# Helper function to trigger webhooks (call from other parts of the app)
async def trigger_webhook_event(event: str, data: dict):
    """Trigger all webhooks subscribed to an event"""
    for webhook_id, webhook in webhooks_store.items():
        if not webhook.get("active", True):
            continue
        if event not in webhook.get("events", []):
            continue
        
        payload = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                if webhook.get("secret"):
                    headers["X-Webhook-Secret"] = webhook["secret"]
                
                await client.post(
                    webhook["url"],
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                
                webhook["last_triggered"] = datetime.now().isoformat()
        except Exception as e:
            print(f"[Webhook] Failed to trigger {webhook_id}: {e}")
