import pandas as pd
from app.db.database import SessionLocal
from app.services.export_service import export_csv
if __name__=="__main__":
    db=SessionLocal()
    try:
        for name in ("videos","video_metrics","engagement_analysis","channel_summary"): print(export_csv(db,name))
    finally: db.close()
