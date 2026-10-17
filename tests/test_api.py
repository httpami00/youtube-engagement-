from fastapi.testclient import TestClient
from app.main import app

def test_docs_and_health():
    c=TestClient(app)
    assert c.get("/api/v1/health").status_code==200
    assert c.get("/docs").status_code==200 and c.get("/redoc").status_code==200
    spec=c.get("/openapi.json").json()
    assert "/api/v1/videos" in spec["paths"] and "/api/v1/analytics/overview" in spec["paths"]

def test_validation_and_errors():
    c=TestClient(app)
    assert c.get("/api/v1/videos?limit=0").status_code==422
    assert c.get("/api/v1/videos?sort_by=bad").status_code==422
    assert c.get("/api/v1/videos/unknown-video").status_code==404
    assert c.get("/api/v1/exports/nope").status_code==404
from fastapi.testclient import TestClient
from app.main import app

def test_root_discovery_links():
    response=TestClient(app).get("/")
    assert response.status_code==200
    assert response.json()["docs"]=="/docs"
