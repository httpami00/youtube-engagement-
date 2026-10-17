from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.models import Video, MetricSnapshot
from app.services.video_service import list_videos
from app.services.analytics_service import overview as calc_overview,publishing_patterns,recommendations
router=APIRouter()
@router.get("/analytics/overview",tags=["Analytics"])
def overview(db:Session=Depends(get_db)): return calc_overview(db)
@router.get("/analytics/top-videos",tags=["Analytics"])
def top_videos(metric:str=Query("views",pattern="^(views|likes|comments|engagement_rate)$"),limit:int=Query(10,ge=1,le=100),db:Session=Depends(get_db)):
    data=list_videos(db,5000,0,None,None,None,"published_at","desc")["items"]
    return sorted((x for x in data if x.get(metric) is not None),key=lambda x:x[metric],reverse=True)[:limit]
@router.get("/analytics/publishing-patterns",tags=["Analytics"])
def patterns(db:Session=Depends(get_db)): return publishing_patterns(db)
@router.get("/analytics/recommendations",tags=["Analytics"])
def recs(db:Session=Depends(get_db)): return recommendations(db)
@router.get("/analytics/growth",tags=["Analytics"])
def growth(db:Session=Depends(get_db)):
    result=[]
    for vid in db.scalars(select(Video.video_id)):
        snaps=list(db.scalars(select(MetricSnapshot).where(MetricSnapshot.video_id==vid).order_by(MetricSnapshot.collected_at,MetricSnapshot.id)))
        for a,b in zip(snaps,snaps[1:]):
            days=(b.collected_at-a.collected_at).total_seconds()/86400
            result.append({"video_id":vid,"from":a.collected_at,"to":b.collected_at,"view_growth":b.views-a.views if a.views is not None and b.views is not None else None,"views_per_day":(b.views-a.views)/days if days>0 and a.views is not None and b.views is not None else None})
    return result
