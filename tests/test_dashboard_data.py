import pandas as pd
from app.dashboard_data import latest_video_frame

def test_latest_snapshot_drives_dashboard_and_missing_values_stay_missing():
    videos=pd.DataFrame([{"video_id":"v1","published_at":"2024-01-01T00:00:00Z","title":"Video"}])
    metrics=pd.DataFrame([
        {"video_id":"v1","collected_at":"2024-01-01T00:00:00Z","views":10,"likes":1,"comments":1},
        {"video_id":"v1","collected_at":"2024-02-01T00:00:00Z","views":100,"likes":None,"comments":2},
    ])
    result=latest_video_frame(videos,metrics).iloc[0]
    assert result.views==100
    assert pd.isna(result.likes)
    assert pd.isna(result.engagement_rate)
