from fastapi import HTTPException
from googleapiclient.discovery import build
import httplib2
from app.core.config import settings

def youtube():
    if not settings.youtube_api_key: raise HTTPException(503,"YOUTUBE_API_KEY is not configured")
    return build("youtube","v3",developerKey=settings.youtube_api_key,cache_discovery=False,http=httplib2.Http(timeout=20))
