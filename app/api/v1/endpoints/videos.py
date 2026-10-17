from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.models import Video, MetricSnapshot
from app.services.video_service import list_videos, latest_snapshot
from app.schemas.video import Page, VideoOut
router=APIRouter()
SORTS={"published_at","title","video_id"}
@router.get("/videos",response_model=Page,tags=["Videos"])
def videos(limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),search:str|None=Query(None,max_length=200),published_after:datetime|None=None,published_before:datetime|None=None,sort_by:str="published_at",sort_order:str=Query("desc",pattern="^(asc|desc)$"),db:Session=Depends(get_db)):
    if sort_by not in SORTS: raise HTTPException(422,"Unsupported sort field")
    if published_after and published_before and published_before<published_after: raise HTTPException(422,"published_before must be on or after published_after")
    return list_videos(db,limit,offset,search,published_after,published_before,sort_by,sort_order)
@router.get("/videos/{video_id}",response_model=VideoOut,tags=["Videos"])
def video(video_id:str,db:Session=Depends(get_db)):
    v=db.get(Video,video_id)
    if not v: raise HTTPException(404,"Video not found")
    s=latest_snapshot(db,video_id)
    return {**{k:getattr(v,k) for k in ["video_id","channel_id","channel_title","title","published_at","duration_seconds","thumbnail_url","url"]},"views":s.views if s else None,"likes":s.likes if s else None,"comments":s.comments if s else None,"engagement_rate":100*(s.likes+s.comments)/s.views if s and s.views and s.likes is not None and s.comments is not None else None}
