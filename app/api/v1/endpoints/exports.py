from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.db.database import get_db
from app.services.export_service import export_csv
router=APIRouter()
@router.get("/exports/{dataset}",tags=["Exports"])
def export(dataset:str,db:Session=Depends(get_db)):
    if dataset not in {"videos","video_metrics","engagement_analysis","channel_summary"}: raise HTTPException(404,"Unknown export dataset")
    path=export_csv(db,dataset)
    return FileResponse(path,media_type="text/csv",filename=f"{dataset}.csv")
