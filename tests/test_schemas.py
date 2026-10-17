from app.schemas.video import CollectionRequest
import pytest

def test_collection_validation():
    assert CollectionRequest(channel_handle="@MrBeast",max_videos=20).max_videos==20
    with pytest.raises(Exception): CollectionRequest(channel_handle="bad handle",max_videos=2)
    with pytest.raises(Exception): CollectionRequest(channel_handle="@MrBeast",max_videos=6000)
