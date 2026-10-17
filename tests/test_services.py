from datetime import datetime, timezone, timedelta
from pathlib import Path
from sqlalchemy import create_engine, select, func, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.database import Base
from app.models import Video, MetricSnapshot
from app.services.video_service import list_videos
from app.services.analytics_service import overview, recommendations
from app.services.export_service import export_csv

engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
Base.metadata.create_all(engine); Session=sessionmaker(engine)
def seed(db,suffix=""):
    vid="vid123"+suffix
    v=Video(video_id=vid,channel_id="channel1",channel_title="Example",title="Test video",published_at=datetime(2024,1,1,tzinfo=timezone.utc),duration_seconds=60,url="https://youtube.com/watch?v="+vid)
    db.add(v); db.flush(); db.add(MetricSnapshot(video_id=v.video_id,collected_at=datetime.now(timezone.utc),views=100,likes=10,comments=2)); db.commit(); return vid
def test_services_and_csv(tmp_path,monkeypatch):
    db=Session(); seed(db)
    result=list_videos(db,10,0,"Test",None,None,"published_at","desc")
    assert result["total"]==1 and result["items"][0]["engagement_rate"]==12
    assert overview(db)["total_views"]==100
    assert "Insufficient" in recommendations(db)[0]["message"]
    monkeypatch.chdir(tmp_path); path=export_csv(db,"video_metrics")
    assert Path(path).read_text(encoding="utf-8").splitlines()[0]=="video_id,collected_at,views,likes,comments"
    db.close()
def test_snapshots_remain_append_only():
    db=Session(); vid=seed(db,"x")
    db.add(MetricSnapshot(video_id=vid,collected_at=datetime.now(timezone.utc)+timedelta(seconds=2),views=120,likes=None,comments=4)); db.commit()
    assert db.scalar(select(func.count()).select_from(MetricSnapshot).where(MetricSnapshot.video_id==vid))==2
    db.close()

from app.services.analytics_service import _median

def test_median_handles_even_and_odd_samples():
    assert _median([1, 3])==2
    assert _median([1, 2, 9])==2
    assert _median([]) is None
