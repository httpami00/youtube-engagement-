from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import MetricSnapshot

class SnapshotRepository:
    def __init__(self, db:Session): self.db=db
    def latest_for_video(self, video_id:str):
        return self.db.scalar(select(MetricSnapshot).where(MetricSnapshot.video_id==video_id).order_by(MetricSnapshot.collected_at.desc(),MetricSnapshot.id.desc()).limit(1))
    def history_for_video(self, video_id:str):
        return list(self.db.scalars(select(MetricSnapshot).where(MetricSnapshot.video_id==video_id).order_by(MetricSnapshot.collected_at,MetricSnapshot.id)))
    def add(self, snapshot:MetricSnapshot):
        self.db.add(snapshot); return snapshot
