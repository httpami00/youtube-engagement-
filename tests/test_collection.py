from datetime import datetime,timezone
from sqlalchemy import create_engine,select,func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
from app.db.database import Base
from app.models import Video,MetricSnapshot
from app.services import collection_service as collector

class Request:
    def __init__(self,value): self.value=value
    def execute(self): return self.value
class Resource:
    def __init__(self,fn): self.fn=fn
    def list(self,**kwargs): return Request(self.fn(**kwargs))
class FakeApi:
    def channels(self): return Resource(lambda **kw:{"items":[{"id":"ch1","snippet":{"title":"MrBeast"},"contentDetails":{"relatedPlaylists":{"uploads":"up1"}}}]})
    def playlistItems(self): return Resource(lambda **kw:{"items":[{"contentDetails":{"videoId":"v1"}},{"contentDetails":{"videoId":"v2"}}]})
    def videos(self): return Resource(lambda **kw:{"items":[{"id":"v1","snippet":{"title":"One","publishedAt":"2024-01-01T00:00:00Z","thumbnails":{}},"contentDetails":{"duration":"PT1H2M3S"},"statistics":{"viewCount":"100","likeCount":"10"}},{"id":"v2","snippet":{"title":"Two","publishedAt":"2024-01-02T00:00:00Z","thumbnails":{}},"contentDetails":{"duration":"PT30S"},"statistics":{"viewCount":"0"}}]})

def test_mocked_collection_persists_nullable_stats(monkeypatch):
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool); Base.metadata.create_all(engine); Session=sessionmaker(engine)
    monkeypatch.setattr(collector,"youtube",lambda:FakeApi()); monkeypatch.setattr(collector,"SessionLocal",Session)
    summary=collector.collect("@MrBeast",2); db=Session()
    assert summary["processed"]==2 and summary["snapshots"]==2
    one=db.get(Video,"v1"); two=db.get(Video,"v2")
    assert one.duration_seconds==3723 and two.duration_seconds==30
    assert db.scalar(select(func.count()).select_from(MetricSnapshot))==2
    assert db.scalar(select(MetricSnapshot.likes).where(MetricSnapshot.video_id=="v2")) is None
    collector.collect("@MrBeast",2)
    assert db.scalar(select(func.count()).select_from(MetricSnapshot))==4
    db.close()

def test_missing_key_is_configuration_error(monkeypatch):
    monkeypatch.setattr(collector,"youtube",lambda:(_ for _ in ()).throw(HTTPException(503,"missing key")))
    try: collector.collect("@MrBeast",1)
    except HTTPException as error: assert error.status_code==503
    else: assert False
