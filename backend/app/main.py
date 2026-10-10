import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.api.routes import router

app = FastAPI(
    title="CityPulse X",
    description="AI-powered urban cascade intelligence system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/")
def dashboard():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {
        "project": "CityPulse X",
        "status": "online",
        "message": "Urban Intelligence System is running"
    }
