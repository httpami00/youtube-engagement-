from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select
from app.models import Video, MetricSnapshot
from app.core.config import settings

def _latest(db):
    result=[]
    for v in db.scalars(select(Video)):
        s=db.scalar(select(MetricSnapshot).where(MetricSnapshot.video_id==v.video_id).order_by(MetricSnapshot.collected_at.desc(),MetricSnapshot.id.desc()).limit(1))
        if s: result.append((v,s))
    return result

def _median(values):
    values=sorted(values)
    if not values: return None
    middle=len(values)//2
    return values[middle] if len(values)%2 else (values[middle-1]+values[middle])/2

def overview(db):
    rows=_latest(db); rates=[100*(s.likes+s.comments)/s.views for _,s in rows if s.views and s.likes is not None and s.comments is not None]
    views=[s.views for _,s in rows if s.views is not None]
    return {"videos_analyzed":len(rows),"total_views":sum(views),"total_likes":sum(s.likes for _,s in rows if s.likes is not None),"total_comments":sum(s.comments for _,s in rows if s.comments is not None),"average_views":sum(views)/len(views) if views else None,"median_views":_median(views),"average_engagement_rate":sum(rates)/len(rates) if rates else None,"median_engagement_rate":_median(rates),"engagement_sample_size":len(rates),"like_count_available":sum(s.likes is not None for _,s in rows),"comment_count_available":sum(s.comments is not None for _,s in rows)}

def publishing_patterns(db):
    groups={}
    tz=ZoneInfo(settings.report_timezone)
    for v,s in _latest(db):
        local=v.published_at.replace(tzinfo=timezone.utc) if v.published_at.tzinfo is None else v.published_at
        local=local.astimezone(tz); key=(local.strftime("%A"),local.hour)
        groups.setdefault(key,[]).append((s.views,100*(s.likes+s.comments)/s.views if s.views and s.likes is not None and s.comments is not None else None))
    return [{"weekday":k[0],"hour":k[1],"sample_size":len(a),"median_views":_median([x[0] for x in a if x[0] is not None]),"median_engagement_rate":_median([x[1] for x in a if x[1] is not None])} for k,a in sorted(groups.items())]

def recommendations(db, minimum=5):
    patterns=publishing_patterns(db); eligible=[x for x in patterns if x["sample_size"]>=minimum and x["median_engagement_rate"] is not None]
    if not eligible:return [{"message":"Insufficient observations to make a reliable recommendation.","evidence":f"Fewer than {minimum} comparable observations per publishing window."}]
    best=max(eligible,key=lambda x:x["median_engagement_rate"])
    return [{"message":f"Observed {best['weekday']} at {best['hour']:02d}:00 has the highest median public engagement in adequately sampled windows.","evidence":f"Median {best['median_engagement_rate']:.3f}% across {best['sample_size']} videos; association only, not causal."}]
