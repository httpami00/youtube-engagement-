from fastapi import APIRouter, HTTPException
from app.schemas.video import CollectionRequest
from app.core.config import settings
router=APIRouter()
@router.post("/collection/run",tags=["Collection"])
def run_collection(request:CollectionRequest):
    if not settings.youtube_api_key: raise HTTPException(503,"YouTube API credentials are not configured. Set YOUTUBE_API_KEY in .env.")
    from app.services.collection_service import collect
    return collect(request.channel_handle,request.max_videos)
