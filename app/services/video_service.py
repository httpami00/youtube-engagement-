from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Video, MetricSnapshot
from app.db.repositories.video_repository import VideoRepository
from app.db.repositories.snapshot_repository import SnapshotRepository

def latest_snapshot(db:Session, video_id:str):
    return SnapshotRepository(db).latest_for_video(video_id)

def list_videos(db:Session, limit:int, offset:int, search:str|None, after:datetime|None, before:datetime|None, sort_by:str, sort_order:str):
    q=select(Video)
    if search: q=q.where(Video.title.ilike(f"%{search}%"))
    if after: q=q.where(Video.published_at>=after)
    if before: q=q.where(Video.published_at<=before)
    repo=VideoRepository(db); total=repo.count(q)
    rows=repo.page(q,getattr(Video,sort_by),sort_order=="desc",limit,offset)
    items=[]
    for v in rows:
        s=latest_snapshot(db,v.video_id)
        er=100*(s.likes+s.comments)/s.views if s and s.views and s.likes is not None and s.comments is not None else None
        items.append({"video_id":v.video_id,"channel_id":v.channel_id,"channel_title":v.channel_title,"title":v.title,"published_at":v.published_at,"duration_seconds":v.duration_seconds,"thumbnail_url":v.thumbnail_url,"url":v.url,"views":s.views if s else None,"likes":s.likes if s else None,"comments":s.comments if s else None,"engagement_rate":er})
    return {"items":items,"total":total,"limit":limit,"offset":offset}
