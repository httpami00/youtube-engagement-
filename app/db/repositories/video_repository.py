from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Video

class VideoRepository:
    def __init__(self, db:Session): self.db=db
    def get(self, video_id:str): return self.db.get(Video,video_id)
    def count(self, query): return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
    def page(self, query, sort_column, descending:bool, limit:int, offset:int):
        order=sort_column.desc() if descending else sort_column.asc()
        return list(self.db.scalars(query.order_by(order).limit(limit).offset(offset)))
