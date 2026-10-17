from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Video

class ChannelRepository:
    def __init__(self, db:Session): self.db=db
    def videos(self, channel_id:str): return list(self.db.scalars(select(Video).where(Video.channel_id==channel_id)))
    def first_video(self): return self.db.scalar(select(Video).limit(1))
