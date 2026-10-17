# Data dictionary
`videos`: video_id (API key), channel_id/title, title, published_at (UTC timestamp), duration_seconds (seconds), thumbnail_url, url. `video_metric_snapshots`: id, video_id, collected_at (UTC), views/likes/comments (nullable integers). Public engagement rate is derived, percent units, requires views > 0 and both counts available. Hidden counts stay null.
