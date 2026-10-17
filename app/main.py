from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter
from app.db.database import Base, engine
from app.models import Video, MetricSnapshot
from app.api.v1.endpoints import health,videos,analytics,collection,exports,channel,dashboard
app=FastAPI(title="YouTube Social Media Engagement Analytics Dashboard",version="1.0.0",description="Analytics based on public YouTube Data API data. Private YouTube Studio metrics are not accessed.",openapi_url="/openapi.json",docs_url="/docs",redoc_url="/redoc")
Base.metadata.create_all(bind=engine)
api=APIRouter(prefix="/api/v1")
for r in [health.router,channel.router,videos.router,analytics.router,collection.router,exports.router,dashboard.router]: api.include_router(r)
app.include_router(api)
@app.get("/",include_in_schema=False)
def root():
    return {"name":app.title,"status":"running","docs":"/docs","redoc":"/redoc","openapi":"/openapi.json","api_prefix":"/api/v1"}
@app.exception_handler(RequestValidationError)
async def validation_error(request:Request,exc:RequestValidationError): return JSONResponse(status_code=422,content={"error":{"code":"validation_error","message":"Request validation failed","details":exc.errors()}})
@app.exception_handler(Exception)
async def unexpected(request:Request,exc:Exception): return JSONResponse(status_code=500,content={"error":{"code":"internal_error","message":"Internal server error"}})

