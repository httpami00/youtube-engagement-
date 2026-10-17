from fastapi import APIRouter
from sqlalchemy import text
from app.db.database import engine
from app.schemas.video import Health
router=APIRouter()
@router.get("/health", response_model=Health, tags=["Health"])
def health():
    try:
        with engine.connect() as connection: connection.execute(text("SELECT 1"))
        return {"status":"ok","database":"available"}
    except Exception as exc:
        return {"status":"degraded","database":"unavailable"}
