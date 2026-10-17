from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
class Video(Base):
    __tablename__ = "videos"
    video_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    channel_title: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text)
    snapshots: Mapped[list["MetricSnapshot"]] = relationship(back_populates="video", cascade="all, delete-orphan")
class MetricSnapshot(Base):
    __tablename__ = "video_metric_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.video_id", ondelete="CASCADE"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    video: Mapped[Video] = relationship(back_populates="snapshots")
