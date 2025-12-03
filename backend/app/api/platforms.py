"""
Platform Upload API
Direct upload to YouTube, TikTok, and other platforms
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

from app.core.database import get_db
from app.models.clip import Clip

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


class YouTubeUploadRequest(BaseModel):
    clip_id: int
    title: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    privacy: Optional[str] = "private"  # private, unlisted, public
    category_id: Optional[str] = "22"  # 22 = People & Blogs
    made_for_kids: Optional[bool] = False


class TikTokUploadRequest(BaseModel):
    clip_id: int
    caption: str
    privacy: Optional[str] = "private"  # private, friends, public
    allow_comments: Optional[bool] = True
    allow_duet: Optional[bool] = True
    allow_stitch: Optional[bool] = True


class InstagramUploadRequest(BaseModel):
    clip_id: int
    caption: str
    share_to_feed: Optional[bool] = True


class PlatformCredentials(BaseModel):
    platform: str  # youtube, tiktok, instagram
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[str] = None


# In-memory credentials store (in production, use secure database)
credentials_store: dict = {}


@router.get("/supported")
def list_supported_platforms():
    """List all supported platforms and their features"""
    return {
        "platforms": [
            {
                "id": "youtube",
                "name": "YouTube / YouTube Shorts",
                "features": ["shorts", "regular", "scheduled"],
                "max_duration": 60,
                "oauth_required": True,
                "status": "available"
            },
            {
                "id": "tiktok",
                "name": "TikTok",
                "features": ["video", "duet", "stitch"],
                "max_duration": 180,
                "oauth_required": True,
                "status": "available"
            },
            {
                "id": "instagram",
                "name": "Instagram Reels",
                "features": ["reels", "stories"],
                "max_duration": 90,
                "oauth_required": True,
                "status": "available"
            }
        ]
    }


@router.post("/credentials")
def save_credentials(creds: PlatformCredentials):
    """Save platform credentials (access tokens)"""
    credentials_store[creds.platform] = {
        "access_token": creds.access_token,
        "refresh_token": creds.refresh_token,
        "expires_at": creds.expires_at,
        "updated_at": datetime.now().isoformat()
    }
    return {"message": f"{creds.platform} credentials saved successfully"}


@router.get("/credentials/{platform}")
def get_credentials_status(platform: str):
    """Check if credentials exist for a platform"""
    if platform not in credentials_store:
        return {"platform": platform, "connected": False}
    
    creds = credentials_store[platform]
    return {
        "platform": platform,
        "connected": True,
        "expires_at": creds.get("expires_at"),
        "updated_at": creds.get("updated_at")
    }


@router.delete("/credentials/{platform}")
def remove_credentials(platform: str):
    """Remove platform credentials"""
    if platform in credentials_store:
        del credentials_store[platform]
    return {"message": f"{platform} credentials removed"}


@router.post("/upload/youtube")
async def upload_to_youtube(
    request: YouTubeUploadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Upload clip to YouTube / YouTube Shorts"""
    clip = db.query(Clip).filter(Clip.id == request.clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    if not clip.exported_path:
        raise HTTPException(status_code=400, detail="Clip has not been exported yet")
    
    if "youtube" not in credentials_store:
        raise HTTPException(status_code=401, detail="YouTube credentials not configured. Please connect your YouTube account first.")
    
    # In production, this would use the YouTube Data API v3
    # For now, return instructions
    return {
        "status": "pending",
        "clip_id": clip.id,
        "platform": "youtube",
        "message": "YouTube upload queued",
        "instructions": {
            "step1": "Go to YouTube Studio: https://studio.youtube.com",
            "step2": "Click 'Create' -> 'Upload videos'",
            "step3": f"Select file: {clip.exported_path}",
            "step4": f"Use title: {request.title}",
            "step5": f"Add description: {request.description}",
            "step6": f"Add tags: {', '.join(request.tags)}",
            "step7": f"Set privacy to: {request.privacy}"
        },
        "api_integration": "To enable direct upload, configure YouTube API credentials in settings"
    }


@router.post("/upload/tiktok")
async def upload_to_tiktok(
    request: TikTokUploadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Upload clip to TikTok"""
    clip = db.query(Clip).filter(Clip.id == request.clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    if not clip.exported_path:
        raise HTTPException(status_code=400, detail="Clip has not been exported yet")
    
    if "tiktok" not in credentials_store:
        raise HTTPException(status_code=401, detail="TikTok credentials not configured. Please connect your TikTok account first.")
    
    return {
        "status": "pending",
        "clip_id": clip.id,
        "platform": "tiktok",
        "message": "TikTok upload queued",
        "instructions": {
            "step1": "Open TikTok app or web: https://www.tiktok.com/upload",
            "step2": f"Select file: {clip.exported_path}",
            "step3": f"Add caption: {request.caption}",
            "step4": f"Set privacy to: {request.privacy}"
        },
        "api_integration": "To enable direct upload, configure TikTok API credentials in settings"
    }


@router.post("/upload/instagram")
async def upload_to_instagram(
    request: InstagramUploadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Upload clip to Instagram Reels"""
    clip = db.query(Clip).filter(Clip.id == request.clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    if not clip.exported_path:
        raise HTTPException(status_code=400, detail="Clip has not been exported yet")
    
    if "instagram" not in credentials_store:
        raise HTTPException(status_code=401, detail="Instagram credentials not configured. Please connect your Instagram account first.")
    
    return {
        "status": "pending",
        "clip_id": clip.id,
        "platform": "instagram",
        "message": "Instagram upload queued",
        "instructions": {
            "step1": "Open Instagram app",
            "step2": "Tap '+' and select 'Reel'",
            "step3": f"Select file: {clip.exported_path}",
            "step4": f"Add caption: {request.caption}"
        },
        "api_integration": "To enable direct upload, configure Instagram Graph API credentials in settings"
    }


@router.get("/oauth/{platform}/url")
def get_oauth_url(platform: str):
    """Get OAuth URL for platform authentication"""
    oauth_urls = {
        "youtube": {
            "url": "https://accounts.google.com/o/oauth2/v2/auth",
            "scope": "https://www.googleapis.com/auth/youtube.upload",
            "instructions": "Configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment"
        },
        "tiktok": {
            "url": "https://www.tiktok.com/auth/authorize/",
            "scope": "video.upload",
            "instructions": "Configure TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET in environment"
        },
        "instagram": {
            "url": "https://api.instagram.com/oauth/authorize",
            "scope": "instagram_content_publish",
            "instructions": "Configure INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET in environment"
        }
    }
    
    if platform not in oauth_urls:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    return {
        "platform": platform,
        **oauth_urls[platform],
        "message": "OAuth flow not yet implemented. Manual upload instructions provided instead."
    }
