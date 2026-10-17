from pathlib import Path
import pandas as pd
from sqlalchemy import select
from app.models import Video, MetricSnapshot

EXPORT_COLUMNS={
 "videos":["video_id","channel_id","channel_title","title","published_at","duration_seconds","thumbnail_url","url"],
 "video_metrics":["video_id","collected_at","views","likes","comments"],
 "engagement_analysis":["video_id","title","collected_at","views","likes","comments","like_rate","comment_rate","engagement_rate"],
 "channel_summary":["channel_id","channel_title","video_count","latest_collected_at","total_views_observed","videos_with_likes","videos_with_comments"]}

def export_csv(db,dataset,output_dir="data/exports"):
    if dataset not in EXPORT_COLUMNS: raise ValueError("Unsupported export dataset")
    root=Path(output_dir); root.mkdir(parents=True,exist_ok=True)
    videos=list(db.scalars(select(Video).order_by(Video.published_at.desc())))
    snapshots=list(db.scalars(select(MetricSnapshot).order_by(MetricSnapshot.collected_at)))
    by_id={v.video_id:v for v in videos}
    if dataset=="videos": rows=[{k:getattr(v,k) for k in EXPORT_COLUMNS[dataset]} for v in videos]
    elif dataset=="video_metrics": rows=[{k:getattr(s,k) for k in EXPORT_COLUMNS[dataset]} for s in snapshots]
    elif dataset=="engagement_analysis":
        rows=[]
        for s in snapshots:
            v=by_id.get(s.video_id); views=s.views
            rows.append({"video_id":s.video_id,"title":v.title if v else None,"collected_at":s.collected_at,"views":views,"likes":s.likes,"comments":s.comments,"like_rate":100*s.likes/views if views and s.likes is not None else None,"comment_rate":100*s.comments/views if views and s.comments is not None else None,"engagement_rate":100*(s.likes+s.comments)/views if views and s.likes is not None and s.comments is not None else None})
    else:
        grouped={}
        for s in snapshots:
            v=by_id.get(s.video_id)
            if v: grouped.setdefault(v.channel_id,{"channel_id":v.channel_id,"channel_title":v.channel_title,"video_count":0,"latest_collected_at":None,"total_views_observed":0,"videos_with_likes":0,"videos_with_comments":0})
            if v:
                row=grouped[v.channel_id]; row["video_count"]+=1
                row["latest_collected_at"]=max(filter(None,[row["latest_collected_at"],s.collected_at]),default=s.collected_at)
                row["total_views_observed"]+=s.views or 0; row["videos_with_likes"]+=s.likes is not None; row["videos_with_comments"]+=s.comments is not None
        rows=list(grouped.values())
        if not rows and videos:
            rows=[{"channel_id":videos[0].channel_id,"channel_title":videos[0].channel_title,"video_count":len(videos),"latest_collected_at":None,"total_views_observed":0,"videos_with_likes":0,"videos_with_comments":0}]
    path=root/f"{dataset}.csv"
    pd.DataFrame(rows,columns=EXPORT_COLUMNS[dataset]).to_csv(path,index=False)
    return path
