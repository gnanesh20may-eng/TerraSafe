"""FastAPI entry point for source-health reporting."""

from fastapi import FastAPI

from backend.app.data_sources import get_source_health

app = FastAPI(
    title="TerraSafe",
    description=(
        "Experimental landslide decision support. Not a replacement for "
        "official IMD, NDMA, or GSI warnings."
    ),
    version="0.1.0",
)


@app.get("/api/v1/health/data-sources", tags=["data"])
def data_source_health():
    """Return registry metadata and latest source-check status."""
    return get_source_health()
