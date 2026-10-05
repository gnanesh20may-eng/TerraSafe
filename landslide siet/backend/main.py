from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.routes import router as api_router
from backend.app.api.sos import router as sos_router
from backend.app.config import APP_NAME, CORS_ALLOWED_ORIGINS, DEMO_MODE
from backend.app.db import init_db
from backend.app.services.environment_service import environment_service


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="AI-based landslide early-warning and rescue intelligence platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(sos_router)


@app.get("/")
def home():
    return {
        "name": APP_NAME,
        "status": "ok",
        "phase": "Phase 5",
        "message": "AI-based landslide early-warning decision-support platform",
        "disclaimer": "This prototype is for decision support only and does not replace official warning guidance.",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "terrasafe-backend",
        "demo_mode": DEMO_MODE,
        "weather_source": "DEMO WEATHER PROVIDER" if DEMO_MODE else type(environment_service.weather_provider).__name__,
        "terrain_source": "DEMO TERRAIN PROVIDER",
        "satellite_source": "DEMO SATELLITE PROVIDER",
    }
