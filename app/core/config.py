from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    youtube_api_key: str | None = None
    channel_handle: str = "@MrBeast"
    max_videos: int = 200
    report_timezone: str = "Asia/Kolkata"
    database_url: str = "sqlite:///./data/youtube_analytics.db"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
