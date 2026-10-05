from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.sos import router as sos_router
from backend.app.api.v1.routes import router as api_router
from backend.app.providers.base import LocationRef
from backend.app.services.environment_service import environment_service

app = FastAPI(
    title="TerraSafe",
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
app.include_router(sos_router)


@app.get("/")
def home():
    return {
        "name": "TerraSafe",
        "status": "ok",
        "phase": "Phase 2",
        "message": "AI-based landslide early-warning decision-support platform",
        "disclaimer": "This prototype is for decision support only and does not replace official warning guidance.",
    }


@app.get("/health")
def health():
    weather = environment_service.weather_provider.get_current_weather(
        LocationRef(
            id="coonor",
            name="Coonoor",
            latitude=11.35,
            longitude=76.8,
            admin_region="Nilgiris District",
        )
    )
    return {
        "status": "ok",
        "service": "terrasafe-backend",
        "demo_mode": weather.source != "open-meteo",
        "weather_source": weather.source,
    }
