"""
PetHospital KPI Service - Main Application

This service collects and displays KPI metrics from multiple
veterinary centers running Codex Veterinaria.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import kpi, dashboard

# Create FastAPI app
app = FastAPI(
    title="PetHospital KPI Service",
    description="Centralized KPI tracking for Codex Veterinaria installations",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Create tables if they do not exist"""
    init_db()
    print("Database initialized")


# Include routers
app.include_router(kpi.router)
app.include_router(dashboard.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "pethospital-kpi"}


@app.get("/api/docs-info")
def api_docs_info():
    """API documentation information"""
    return {
        "openapi_url": "/openapi.json",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "submit_metrics": "POST /kpi/submit",
            "list_centers": "GET /kpi/centers",
            "get_metrics": "GET /kpi/centers/{code}/metrics",
            "summary_stats": "GET /kpi/stats/summary",
            "dashboard": "GET /"
        }
    }
