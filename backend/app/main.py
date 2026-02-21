from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import health, trip_searches, recommendations, playbook, alerts

load_dotenv()

app = FastAPI(title="PointsTrip Optimizer API", version="0.1.0")

app.include_router(health.router, tags=["health"])
app.include_router(trip_searches.router, prefix="/v1/trip-searches", tags=["trip-searches"])
app.include_router(recommendations.router, prefix="/v1/recommendations", tags=["recommendations"])
app.include_router(playbook.router, prefix="/v1/playbook", tags=["playbook"])
app.include_router(alerts.router, prefix="/v1/alerts", tags=["alerts"])
