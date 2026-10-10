from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="CityPulse X",
    description="AI-powered urban cascade intelligence system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "project": "CityPulse X",
        "status": "online",
        "message": "Urban Intelligence System is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }