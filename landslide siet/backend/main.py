from backend.app.routes.geocode import router as geocode_router
from backend.app.routes.weather import router as weather_router
from backend.app.routes.elevation import router as elevation_router
from backend.app.routes.satellite import router as satellite_router
from backend.app.routes.precipitation import router as precipitation_router
from backend.app.routes.gibs import router as gibs_router
from backend.app.routes.lhasa import router as lhasa_router
from backend.app.routes.bhuvan import router as bhuvan_router
from backend.app.routes.ndem import router as ndem_router
from backend.app.routes.osm import router as osm_router
from backend.app.routes.risk import router as risk_router
from backend.app.routes.zones import router as zones_router
from backend.app.routes.simulation import router as simulation_router
from backend.app.routes.copilot import router as copilot_router
from backend.app.routes.trends import router as trends_router
from backend.app.routes.vulnerable import router as vulnerable_router
from backend.app.routes.priority import router as priority_router
from backend.app.routes.response_plan import router as response_plan_router
from backend.app.routes.analysis import router as analysis_router
from backend.app.routes.health import router as health_router
from backend.app.config import APP_NAME
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(geocode_router)
app.include_router(weather_router)
app.include_router(elevation_router)
app.include_router(satellite_router)
app.include_router(precipitation_router)
app.include_router(gibs_router)
app.include_router(lhasa_router)
app.include_router(bhuvan_router)
app.include_router(ndem_router)
app.include_router(osm_router)
app.include_router(risk_router)
app.include_router(zones_router)
app.include_router(simulation_router)
app.include_router(copilot_router)
app.include_router(trends_router)
app.include_router(vulnerable_router)
app.include_router(priority_router)
app.include_router(response_plan_router)
app.include_router(analysis_router)
app.include_router(health_router)

@app.get("/")
def home():
    return {
        "name": APP_NAME,
        "status": "ok",
        "message": "AI-based landslide early-warning prototype",
        "disclaimer": "AI-generated decision-support alert. This prototype does not replace official disaster-management warnings.",
    }

@app.get("/health")
def health():
    return {"status": "ok"}
