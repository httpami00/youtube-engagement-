from pathlib import Path

import pandas as pd

EXPORT_DIR = Path(__file__).resolve().parents[1] / "data" / "exports"


def read_exports(directory: Path = EXPORT_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    def read(name: str) -> pd.DataFrame:
        path = directory / f"{name}.csv"
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    return read("videos"), read("video_metrics"), read("engagement_analysis")


def latest_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return metrics.copy()
    frame = metrics.copy()
    frame["collected_at"] = pd.to_datetime(frame["collected_at"], utc=True, errors="coerce")
    return frame.sort_values("collected_at").drop_duplicates("video_id", keep="last")


def latest_video_frame(videos: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    if videos.empty:
        return pd.DataFrame()
    frame = videos.merge(latest_metrics(metrics), on="video_id", how="left", suffixes=("", "_metric"))
    if "published_at" in frame:
        frame["published_at"] = pd.to_datetime(frame["published_at"], utc=True, errors="coerce")
    denominator = frame["views"].where(frame["views"].gt(0))
    frame["like_rate"] = 100 * frame["likes"] / denominator
    frame["comment_rate"] = 100 * frame["comments"] / denominator
    frame["engagement_rate"] = 100 * (frame["likes"] + frame["comments"]) / denominator
    return frame
