from app.db.database import Base, engine
from app.models import Video, MetricSnapshot
if __name__=="__main__":
    Base.metadata.create_all(engine)
    print("Set YOUTUBE_API_KEY then use POST /api/v1/collection/run to collect public API records.")
