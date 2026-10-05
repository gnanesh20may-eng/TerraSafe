# System Architecture

## 1. Product architecture

LandSense follows a four-layer decision-support architecture:

1. Data acquisition
   - Weather and precipitation providers
   - Terrain and DEM sources
   - Satellite and vegetation inputs
   - Hydrological and soil context
2. Geospatial intelligence
   - Feature generation
   - Terrain conditioning
   - Risk-zone overlays
   - Safe-zone and route abstraction
3. ML and inference
   - Susceptibility model
   - Trigger model
   - Risk normalization and alert thresholds
   - SHAP explanations and model registry
4. Operational response
   - API layer
   - Monitoring dashboard
   - Rescue hub
   - Alert engine and notifications

## 2. Runtime architecture

```text
User / Browser
     |
     v
Next.js Frontend
     |
     | REST + SSE/WebSocket
     v
FastAPI Backend
     |
     +--> Authentication + Authorization
     +--> Risk API + Alert API
     +--> Provider adapters
     +--> ML inference service
     +--> Spatial and route services
     |
     v
PostgreSQL + PostGIS
     |
     +--> locations
     +--> monitored_locations
     +--> weather_observations
     +--> terrain_features
     +--> risk_predictions
     +--> alerts
     +--> safe_zones
     +--> routes
     |
     v
Redis + APScheduler
     |
     +--> alert queue
     +--> cache
     +--> scheduled refreshes
```

## 3. Database ER diagram

```text
users
  - id (PK)
  - name
  - email
  - role
  - password_hash
  - created_at

locations
  - id (PK)
  - name
  - geography (GEOGRAPHY/POINT)
  - latitude
  - longitude
  - admin_region
  - elevation_m
  - created_at

monitored_locations
  - id (PK)
  - user_id (FK)
  - location_id (FK)
  - alert_radius_km
  - alert_enabled
  - threshold
  - created_at

environmental_observations
  - id (PK)
  - location_id (FK)
  - rainfall_1h_mm
  - rainfall_6h_mm
  - rainfall_24h_mm
  - rainfall_7d_mm
  - soil_moisture
  - wind_speed
  - temperature_c
  - pressure_hpa
  - source
  - observed_at

terrain_features
  - id (PK)
  - location_id (FK)
  - elevation_m
  - slope_deg
  - aspect_deg
  - curvature
  - ruggedness
  - ndvi
  - land_cover
  - drainage_index
  - created_at

risk_predictions
  - id (PK)
  - location_id (FK)
  - susceptibility_score
  - trigger_score
  - final_score
  - risk_level
  - confidence
  - model_version
  - prediction_time

risk_factors
  - id (PK)
  - prediction_id (FK)
  - factor_name
  - impact
  - direction
  - contribution

alerts
  - id (PK)
  - location_id (FK)
  - risk_state
  - alert_state
  - severity
  - message
  - created_at
  - acknowledged_at
  - resolved_at

alert_events
  - id (PK)
  - alert_id (FK)
  - previous_state
  - next_state
  - event_type
  - created_at

safe_zones
  - id (PK)
  - name
  - geography (POINT)
  - type
  - capacity
  - address
  - contact
  - availability
  - verification_status

emergency_contacts
  - id (PK)
  - location_id (FK)
  - name
  - organization
  - phone
  - role
  - verification_status

routes
  - id (PK)
  - origin_location_id (FK)
  - destination_zone_id (FK)
  - route_geometry (GEOMETRY/LINESTRING)
  - safety_score
  - routing_method
  - created_at

model_versions
  - id (PK)
  - name
  - version
  - registered_at
  - metadata

data_sources
  - id (PK)
  - source_name
  - source_type
  - provider
  - last_update

audit_logs
  - id (PK)
  - user_id (FK)
  - action
  - resource
  - metadata
  - created_at
```

## 4. Frontend page architecture

```text
/
  Home page
  - hero + location search
  - map preview
  - risk summary
  - CTAs to evaluation and rescue hub

/evaluation
  - selected area details
  - environmental signals
  - risk score and level
  - AI explanation
  - recommendation
  - trend summary

/rescue-hub
  - emergency-focused layout
  - current risk + safe zones
  - safe route summary
  - emergency contacts
  - Get Help CTA

/alerts
  - history and current status

/settings
  - alerts, notifications, display preferences

/about
  - system, data, model, and limitations
```

## 5. Backend API architecture

```text
/api/v1
├── /health
├── /auth/login
├── /auth/profile
├── /locations/search
├── /locations/{id}
├── /risk/{location_id}
├── /risk/{location_id}/history
├── /environment/{location_id}
├── /terrain/{location_id}
├── /map/risk-zones
├── /safe-zones
├── /rescue/nearby
├── /rescue/route
├── /alerts
├── /alerts/preferences
├── /data-sources
├── /models
└── /admin
```

## 6. ML pipeline architecture

The platform separates long-term susceptibility from current trigger risk:

- Model A: susceptibility
  - terrain slope, elevation, aspect, curvature, soil, geology, land cover, historical landslides
- Model B: trigger risk
  - rainfall accumulation, recent precipitation anomalies, soil moisture, weather forecast, terrain wetness indicators

These are combined into the final normalized 0-100 risk score with configurable thresholds.

## 7. GIS pipeline architecture

- Raster and vector data ingestion
- Terrain and drainage feature generation
- Spatial joins with landslide history and infrastructure data
- Risk-zone polygon generation
- Safe-zone and evacuation route overlays

## 8. Folder structure

```text
landslide siet/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── lib/
│   ├── services/
│   ├── types/
│   └── tests/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── providers/
│   │   ├── ml/
│   │   ├── gis/
│   │   └── main.py
│   └── tests/
├── ml/
├── gis/
├── docs/
├── scripts/
├── docker/
├── .github/workflows/
├── docker-compose.yml
├── .env.example
├── README.md
├── requirements.txt
└── LICENSE
```

## 9. Development roadmap

### Phase 1
- monorepo and project architecture
- backend and frontend skeletons
- Docker and CI scaffolding
- auth foundation
- health and config endpoints

### Phase 2
- home page, location search, map integration
- selected location state and risk summary card

### Phase 3
- weather, terrain, and satellite provider adapters

### Phase 4
- GIS feature engineering and risk-zone generation

### Phase 5
- ML model training, validation, SHAP, MLflow

### Phase 6
- risk API, evaluation view, recommendations

### Phase 7
- alert engine and notifications

### Phase 8
- rescue hub, safe zones, routing abstraction

### Phase 9
- authority dashboard and admin views

### Phase 10
- hardening, performance, security, and deployment

## 10. Required dependencies

### Runtime
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- MapLibre GL JS
- FastAPI
- PostgreSQL + PostGIS
- Redis
- APScheduler
- Pydantic
- SQLAlchemy
- GeoPandas
- Rasterio
- GDAL
- xarray
- pandas
- numpy
- scikit-learn
- XGBoost
- LightGBM
- SHAP
- MLflow

### Dev and testing
- pytest
- Playwright
- Ruff
- ESLint
- TypeScript compiler
- Docker
- GitHub Actions
