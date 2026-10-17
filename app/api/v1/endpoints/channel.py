from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.models import Video
router=APIRouter()
@router.get("/channel",tags=["Channel"])
def channel(db:Session=Depends(get_db)):
    video=db.scalar(select(Video).limit(1))
    if not video: raise HTTPException(404,"No channel data is stored yet; run collection first")
    return {"channel_id":video.channel_id,"channel_title":video.channel_title,"handle":"@MrBeast" if video.channel_title.lower()=="mrbeast" else None,"source":"stored video metadata"}
