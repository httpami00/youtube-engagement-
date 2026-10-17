# Power BI data model and import
Import `videos.csv`, `video_metrics.csv`, `engagement_analysis.csv`, and `channel_summary.csv`. Keep the table names as imported or rename them consistently; DAX measures use `Videos`, `VideoMetrics`, `EngagementAnalysis`, and `ChannelSummary`.

## Relationships (important)
`videos.csv` has one row per video, so `Videos[video_id]` is the unique lookup/dimension key (the **1** side). `video_metrics.csv` and `engagement_analysis.csv` contain dated observations and therefore intentionally repeat `video_id` (the **many** side). Create single-direction one-to-many relationships:

- `Videos[video_id]` **1 → many** `VideoMetrics[video_id]`
- `Videos[video_id]` **1 → many** `EngagementAnalysis[video_id]`

Do not put `video_metrics[video_id]` or `engagement_analysis[video_id]` on the 1 side, and do not relate those two snapshot tables directly. Remove any automatically created relationships that reverse this direction. Leave `ChannelSummary` disconnected unless you build a separate unique channel dimension.

In Model view, delete the incorrect relationship line, then drag `Videos[video_id]` onto the matching fact-table `video_id`; in the dialog choose **One to many (1:*)**, with `Videos` on the 1 side and single cross-filter direction. If Power BI says `Videos[video_id]` itself has duplicates, check that `videos.csv` is loaded from the project export, because this table should contain one row per video.

## Export schemas
`videos.csv`: video_id, channel_id, channel_title, title, published_at, duration_seconds, thumbnail_url, url.
`video_metrics.csv`: video_id, collected_at, views, likes, comments (one row per dated observation).
`engagement_analysis.csv`: video_id, title, collected_at, views, likes, comments, like_rate, comment_rate, engagement_rate.
`channel_summary.csv`: channel_id, channel_title, video_count, latest_collected_at, total_views_observed, videos_with_likes, videos_with_comments. `video_count` here counts metric observations, not distinct uploads.

Parse timestamps as Date/Time (UTC). Rate columns are percentage-point values (e.g. 12 means 12%); format them as percentages without multiplying again. Null metrics mean unavailable, not zero. The exports reflect stored data only.
