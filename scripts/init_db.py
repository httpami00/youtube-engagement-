from app.db.database import Base, engine
from app.models import Video, MetricSnapshot
Base.metadata.create_all(engine)
print("Database initialized")
