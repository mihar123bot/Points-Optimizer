from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import health, trip_searches, recommendations, playbook, alerts

load_dotenv()

app = FastAPI(title="PointPilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(trip_searches.router, prefix="/v1/trip-searches", tags=["trip-searches"])
app.include_router(recommendations.router, prefix="/v1/recommendations", tags=["recommendations"])
app.include_router(playbook.router, prefix="/v1/playbook", tags=["playbook"])
app.include_router(alerts.router, prefix="/v1/alerts", tags=["alerts"])
