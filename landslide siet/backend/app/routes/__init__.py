from fastapi import APIRouter
from backend.app.routes.alerts import router as alerts_router
from backend.app.routes.analysis import router as analysis_router
from backend.app.routes.bhuvan import router as bhuvan_router
from backend.app.routes.copilot import router as copilot_router
from backend.app.routes.elevation import router as elevation_router
from backend.app.routes.gibs import router as gibs_router
from backend.app.routes.geocode import router as geocode_router
from backend.app.routes.health import router as health_router
from backend.app.routes.lhasa import router as lhasa_router
from backend.app.routes.ndem import router as ndem_router
from backend.app.routes.osm import router as osm_router
from backend.app.routes.precipitation import router as precipitation_router
from backend.app.routes.priority import router as priority_router
from backend.app.routes.response_plan import router as response_plan_router
from backend.app.routes.risk import router as risk_router
from backend.app.routes.satellite import router as satellite_router
from backend.app.routes.simulation import router as simulation_router
from backend.app.routes.trends import router as trends_router
from backend.app.routes.vulnerable import router as vulnerable_router
from backend.app.routes.weather import router as weather_router
from backend.app.routes.zones import router as zones_router

router = APIRouter()

router.include_router(geocode_router)
router.include_router(weather_router)
router.include_router(elevation_router)
router.include_router(satellite_router)
router.include_router(precipitation_router)
router.include_router(gibs_router)
router.include_router(lhasa_router)
router.include_router(bhuvan_router)
router.include_router(ndem_router)
router.include_router(osm_router)
router.include_router(risk_router)
router.include_router(alerts_router)
router.include_router(health_router)
router.include_router(zones_router)
router.include_router(simulation_router)
router.include_router(copilot_router)
router.include_router(trends_router)
router.include_router(vulnerable_router)
router.include_router(priority_router)
router.include_router(response_plan_router)
router.include_router(analysis_router)
