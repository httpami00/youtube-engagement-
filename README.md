# YouTube Social Media Engagement Analytics Dashboard
A locally run FastAPI analytics system for public YouTube video data. The pipeline is MrBeast public channel → official YouTube Data API v3 → Python/Pandas normalization → SQLite video metadata and append-only dated metric snapshots → CSV exports → FastAPI analytics → Power BI. It never claims access to private creator Studio reports.

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Add your own YouTube API key in .env, then:
python -m scripts.init_db
python -m uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs. ReDoc: `/redoc`; schema: `/openapi.json`.

## Collect and export
Configure YOUTUBE_API_KEY in local `.env`. Create a Google Cloud project, enable YouTube Data API v3, and create a key using https://developers.google.com/youtube/v3/getting-started. Then call `POST /api/v1/collection/run` with `{"channel_handle":"@MrBeast","max_videos":200}`. Collector resolves the channel, paginates uploads, fetches details in batches, validates/normalizes with Pandas, commits videos and timestamped metric snapshots transactionally. Missing statistics stay null. Export all four CSV files with:
```powershell
python -m scripts.export_data
```
Files land under `data/exports/`. Empty database exports contain headers only; no sample data is fabricated.

## API
`GET /api/v1/health`, `/api/v1/channel`, `/api/v1/videos`, `/api/v1/videos/{video_id}`, `/api/v1/analytics/overview`, `/api/v1/analytics/top-videos`, `/api/v1/analytics/publishing-patterns`, `/api/v1/analytics/growth`, `/api/v1/analytics/recommendations`, `POST /api/v1/collection/run`, `GET /api/v1/exports/{videos|video_metrics|engagement_analysis|channel_summary}`.

## Analytics and dashboard
Public engagement rate = (likes + comments) / views × 100 only when both counts exist and views > 0. Growth uses actual separate snapshots. Read `powerbi/data_model.md`, `powerbi/measures.dax`, and `powerbi/dashboard_guide.md` for imports and four report pages. PBIX creation requires Power BI Desktop and is manual.

## Tests
```powershell
python -m pytest -q -p no:cacheprovider
```
Tests mock YouTube API calls; they do not spend quota or represent live channel findings. See docs/ for system architecture, database dictionary, methodology, limitations, and report outline. API rules: https://developers.google.com/youtube/terms/api-services-terms-of-service.
