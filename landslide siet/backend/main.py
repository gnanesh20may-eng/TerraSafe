from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.routes import router as api_router

app = FastAPI(
    title="LandSense",
    version="1.0.0",
    description="AI-based landslide early-warning and rescue intelligence platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def home():
    return {
        "name": "LandSense",
        "status": "ok",
        "phase": "Phase 2",
        "message": "AI-based landslide early-warning decision-support platform",
        "disclaimer": "This prototype is for decision support only and does not replace official warning guidance.",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "landsense-backend",
        "demo_mode": True,
    }
