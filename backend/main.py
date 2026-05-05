from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.core.database import engine, Base
from backend.api import users, vehicles, auth, sensors, visualization, dashboard, alerts, reports, predictions, agent_router, service_schedules, notifications

app = FastAPI(
    title="Automotive Predictive Maintenance API",
    description="Intelligent vehicle maintenance prediction system with real-time sensor monitoring",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 Startup event
@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            # ✅ Create tables automatically
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Database connected successfully")
        print("✅ All tables created/updated")
    except Exception as e:
        print("❌ DB connection failed:", e)

# ✅ Root endpoint
@app.get("/")
async def root():
    return {
        "message": "🚗 Automotive Predictive Maintenance API v2.0",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "User Authentication & JWT",
            "Vehicle Management",
            "Real-time Sensor Data Ingestion",
            "Data Visualization & Analytics",
            "Predictive Maintenance Engine (ML v4)"
        ]
    }

# ✅ Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}

# ✅ Register routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(visualization.router, prefix="/viz", tags=["Visualization"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(agent_router.router, prefix="/agents", tags=["Agents"])
app.include_router(service_schedules.router, prefix="/service-schedules", tags=["Service Schedules"])
app.include_router(notifications.router, tags=["Notifications"])