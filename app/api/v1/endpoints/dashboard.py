from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
router=APIRouter()
@router.get("/dashboard",tags=["Dashboard"],summary="Open the generated local analytics dashboard")
def dashboard():
    path=Path("data/exports/dashboard.html")
    if not path.exists(): raise HTTPException(404,"Dashboard file not generated; run python -m scripts.build_dashboard")
    return FileResponse(path,media_type="text/html")
