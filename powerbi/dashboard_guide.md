# Power BI layout matching the supplied reference
Use a 16:9 canvas, dark charcoal page background, white typography, and cyan/blue chart accents. Keep a compact report header with title and channel label.

## Top KPI strip
Arrange seven cards across the top: Videos Analyzed, Total Views (Latest), Average Engagement Rate (Latest), Total Comments (Latest), Total Likes (Latest), Average Like Rate (Latest), Average Comment Rate (Latest). Do not sum per-video rates. Add a channel slicer only if more than one channel is loaded.

## Main charts
- Upper left: line chart titled “Views by Publishing Month”; use a month hierarchy from Videos[published_at], and plot latest views per video only when the intended meaning is upload cohort performance. For actual time-series growth, use VideoMetrics[collected_at] on the axis and `Views by Snapshot Date` as values. Do not label a snapshot date chart as publishing month.
- Upper right: horizontal bar chart of top 10 videos by latest views. Axis: Videos[title], value: Total Views (Latest), visual filter Top N 10 by the measure, descending.
- Lower left: table with title, latest engagement rate, latest views, likes, comments. Use the three latest-rate measures and latest totals.
- Lower middle: year comparison of average engagement rate by publication year. Add year from published_at and use Average Engagement Rate (Latest); a pie chart can match the reference, though clustered column is easier to compare.
- Lower right: interaction coverage donut with three counts: videos with views, videos with available likes, videos with available comments. Use distinct video counts; do not sum percentages or treat missing values as zero.

Use these measures from `powerbi/measures.dax` for the interaction coverage donut: `Videos With Views (Latest)`, `Videos With Likes (Latest)`, and `Videos With Comments (Latest)`. Add all three as values. They count each distinct video once using its newest stored observation, and exclude unavailable metrics. Do not use `Count of video_id` from either snapshot table, because that counts observations and repeats a video when it has multiple collection dates.

## Model
Videos is the unique lookup table. Relate Videos[video_id] (1) to VideoMetrics[video_id] (*) and EngagementAnalysis[video_id] (*). Snapshot IDs repeat intentionally. Keep ChannelSummary disconnected. Use single-direction filter propagation from Videos to facts.

`powerbi/measures.dax` has measures that select each video's latest stored metric snapshot for KPI and ranking visuals. `Views by Snapshot Date` deliberately sums observations and is intended only for a date-axis trend where multiple snapshots exist. Publishing-month and year analysis use the video publication timestamp, grouped by upload date. Public metrics only; no private Studio analytics.
