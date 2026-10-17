from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, model_validator
from typing import Generic, TypeVar
T=TypeVar("T")
class CollectionRequest(BaseModel):
    channel_handle: str = Field(default="@MrBeast", min_length=3, max_length=100, pattern=r"^@?[A-Za-z0-9._-]+$")
    max_videos: int = Field(default=200, ge=1, le=5000)
class VideoOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    video_id:str; channel_id:str; channel_title:str; title:str; published_at:datetime
    duration_seconds:int|None; thumbnail_url:str|None; url:str
    views:int|None=None; likes:int|None=None; comments:int|None=None; engagement_rate:float|None=None
class Page(BaseModel):
    items:list[VideoOut]; total:int; limit:int; offset:int
class Health(BaseModel): status:str; database:str
class CollectionSummary(BaseModel): channel_id:str; discovered:int; processed:int; snapshots:int; collected_at:datetime; warnings:list[str]
