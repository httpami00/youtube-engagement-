from datetime import datetime, timezone
from fastapi import HTTPException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from app.core.config import settings
from app.db.database import SessionLocal
from app.models import Video, MetricSnapshot
from app.services.youtube_client import youtube
import pandas as pd
from datetime import timedelta
from sqlalchemy import delete

def collect(handle, limit):
    api=youtube()
    try:
        channel=api.channels().list(part="snippet,contentDetails,statistics",forHandle=handle.lstrip("@")).execute()
        if not channel.get("items"): raise HTTPException(404,"YouTube channel not found")
        ch=channel["items"][0]; cid=ch["id"]; title=ch["snippet"]["title"]; uploads=ch["contentDetails"]["relatedPlaylists"]["uploads"]
        ids=[]; token=None
        while len(ids)<limit:
            page=api.playlistItems().list(part="contentDetails",playlistId=uploads,maxResults=min(50,limit-len(ids)),pageToken=token).execute()
            ids.extend(x["contentDetails"]["videoId"] for x in page.get("items",[])); token=page.get("nextPageToken")
            if not token: break
        now=datetime.now(timezone.utc); processed=0; warnings=[]; records=[]
        for start in range(0,len(ids),50):
            batch=api.videos().list(part="snippet,contentDetails,statistics",id=",".join(ids[start:start+50])).execute()
            records.extend(batch.get("items",[]))
        if len(records)<len(ids): warnings.append(f"{len(ids)-len(records)} discovered videos were unavailable in video details.")
        normalized=[]
        for x in records:
            try:
                s=x["snippet"]; st=x.get("statistics",{})
                normalized.append({"id":x["id"],"channel_id":cid,"channel_title":title,"title":s["title"],"published_at":datetime.fromisoformat(s["publishedAt"].replace("Z","+00:00")),"duration_seconds":_duration_seconds(x.get("contentDetails",{}).get("duration")),"thumbnail_url":s.get("thumbnails",{}).get("high",{}).get("url"),"views":int(st["viewCount"]) if "viewCount" in st else None,"likes":int(st["likeCount"]) if "likeCount" in st else None,"comments":int(st["commentCount"]) if "commentCount" in st else None})
            except (KeyError,TypeError,ValueError): warnings.append(f"Skipped malformed video record {x.get('id','unknown')}.")
        frame=pd.DataFrame(normalized)
        db=SessionLocal()
        try:
            # Public statistics are non-authorized API data and are retained for at most 30 days.
            db.execute(delete(MetricSnapshot).where(MetricSnapshot.collected_at < now - timedelta(days=30)))
            for row in frame.to_dict(orient="records"):
                v=db.get(Video,row["id"])
                if not v: v=Video(video_id=row["id"],channel_id=cid,channel_title=title,title=row["title"],published_at=row["published_at"],url=f"https://www.youtube.com/watch?v={row['id']}"); db.add(v)
                v.channel_id=cid; v.channel_title=title; v.title=row["title"]; v.thumbnail_url=row["thumbnail_url"]; v.published_at=row["published_at"]; v.duration_seconds=row["duration_seconds"]
                v.snapshots.append(MetricSnapshot(collected_at=now,views=row["views"],likes=row["likes"],comments=row["comments"])); processed+=1
            db.commit()
        finally: db.close()
        return {"channel_id":cid,"discovered":len(ids),"processed":processed,"snapshots":processed,"collected_at":now,"warnings":warnings}
    except HTTPException: raise
    except HttpError as e:
        code=getattr(e.resp,"status",502)
        raise HTTPException(503 if code==403 else 502,"YouTube API request failed; check API key, quota, and API enablement")
    except Exception as e: raise HTTPException(502,"YouTube collection failed") from e

def _duration_seconds(value):
    if not value: return None
    match=re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",value)
    if not match: return None
    hours,minutes,seconds=(int(x or 0) for x in match.groups())
    return hours*3600+minutes*60+seconds
