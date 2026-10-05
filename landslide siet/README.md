# LandSense - AI-Powered Landslide Early Warning & Risk Monitoring System

## Overview

LandSense is an **Explainable AI Landslide Risk Decision-Support and Scenario Simulation Platform** designed for disaster management and early warning.

This is a **prototype system** for educational and demonstration purposes. It provides:
- AI-based risk estimation (not official prediction)
- Early-warning decision support
- Explainable risk scoring
- What-if rainfall simulation
- Interactive GIS micro-zone mapping
- Conversational AI Copilot
- Risk trend analysis
- Alert history tracking
- Multilingual UI (English/Tamil)

**DISCLAIMER:** This prototype does not replace official disaster-management warnings or government forecasts.

---

## Features

### 1. Explainable AI Risk Score (0-100)
- Real-time risk calculation from multiple factors:
  - Rainfall (1h/3h/6h/24h/72h)
  - Soil moisture
  - Slope degree
  - Vegetation stability (NDVI)
  - Historical landslide density
- Factor contribution visualization (percentages)
- Clear explanation: "Why is this zone at risk?"

### 2. What-If Rainfall Simulator
- Interactive sliders for:
  - Rainfall amount
  - Soil moisture
  - Slope
- Real-time risk recalculation
- Visual feedback: risk transitions from MODERATE → HIGH → CRITICAL
- Pre-built scenarios:
  - Normal Rainfall
  - Heavy Rainfall
  - Extreme Rainfall

### 3. Micro-Zone Risk Map
- Interactive Leaflet/OpenStreetMap GIS
- 4 zones with live risk visualization:
  - Zone A (Wayanad): CRITICAL
  - Zone B (Nilgiris): MODERATE
  - Zone C (Darjeeling): CRITICAL
  - Zone D (Kodaikanal): LOW
- Color-coded risk levels:
  - 🟢 GREEN = LOW (0-30)
  - 🟡 YELLOW = MODERATE (31-60)
  - 🟠 ORANGE = HIGH (61-80)
  - 🔴 RED = CRITICAL (81-100)
- Click zones for detail panel with:
  - Risk score
  - Rainfall, soil moisture, slope
  - Historical incidents
  - Recommended actions

### 4. Risk Trend Chart
- Time-series visualization of risk over 12 hours
- Shows:
  - Current risk (peak)
  - Previous risk (trend)
  - Projected/estimated future risk
- Area chart with gradient (high risk = red)

### 5. False-Alarm Reduction
- CRITICAL alert requires **multiple supporting conditions**
- Alert confidence scoring:
  - Low confidence: single high factor
  - High confidence (91%): rainfall + moisture + slope alignment
- Example: "Heavy rainfall" alone ≠ CRITICAL
  - But: Heavy rainfall + high soil moisture + steep slope = CRITICAL (91% confidence)

### 6. Smart Early Warning System
- Automatic alert generation at risk thresholds:
  - 0-30: LOW
  - 31-60: MODERATE
  - 61-80: HIGH
  - 81-100: CRITICAL
- Alert includes:
  - Zone name
  - Risk score and level
  - Main triggering factors
  - Recommended action
  - Timestamp
  - Status (active/monitoring)

### 7. AI Copilot (Rule-Based)
- **Landsafe Copilot** conversational interface
- Answers questions using live application data:
  - "Which zones are currently critical?" → Data-driven answer
  - "Why is Zone A dangerous?" → Explains current risk factors
  - "What happens if rainfall increases to 180 mm?" → Simulation-based answer
  - "Which zones are safest?" → Ranks zones by current risk
  - "Which area should be inspected first?" → Priority-based recommendation
- **IMPORTANT:** AI never invents numbers; all answers use app data

### 8. Counterfactual Explanation
- "What would reduce the risk?"
- System shows:
  - "Risk could fall below critical threshold if..."
  - "Rainfall intensity decreases"
  - "Soil moisture returns to moderate levels"
  - "Slope remains manageable"

### 9. Vulnerable Location Priority
- Detects nearby critical infrastructure:
  - Schools, hospitals, roads, bridges, settlements
- Priority classification:
  - **Priority 1 – Immediate attention** (near CRITICAL zones)
  - **Priority 2 – Monitor** (near HIGH zones)
  - **Priority 3 – Low priority** (near MODERATE/LOW zones)
- Shows on map and in response plan

### 10. Safe Route & Response Recommendations
- Automatic response plan:
  - "Avoid Zone A road"
  - "Inspect Zone B cut slopes"
  - "Monitor Zone C with evacuation prep"
  - "Maintain routine monitoring in Zone D"

### 11. Incident/Alert History
- Stores all alerts with:
  - Timestamp
  - Zone name
  - Risk score
  - Trigger reason (e.g., "Heavy rainfall + steep slope")
  - Alert level
  - Action/status
- Reviewable table of historical events

### 12. Multilingual Support
- English / Tamil (தமிழ்)
- Critical warnings translated
- Example:
  - EN: "Critical landslide risk detected in Zone A."
  - TA: "Zone A பகுதியில் நிலச்சரிவு அபாயம் மிக அதிகமாக உள்ளது."

---

## Architecture

### Backend (Python/FastAPI)

**File structure:**
```
landslide siet/backend/
├── main.py                          # FastAPI app entry point
├── app/
│   ├── __init__.py
│   ├── config.py                    # Environment config
│   ├── cache.py                     # TTL cache layer
│   ├── models.py                    # Data models
│   ├── risk_engine.py               # Core risk scoring (weighted)
│   ├── demo_data.py                 # Demo zones (Ooty, Wayanad, etc.)
│   ├── explainer.py                 # Explainable AI (factor breakdown)
│   ├── simulator.py                 # What-if simulation engine
│   ├── alert_manager.py             # Alert generation logic
│   ├── trend_tracker.py             # Risk trend history
│   ├── zone_data.py                 # Micro-zone data
│   ├── vulnerable_locations.py      # Schools, hospitals, roads
│   ├── priority_summary.py          # Priority classification
│   ├── routes/                      # API endpoints
│   │   ├── geocode.py
│   │   ├── weather.py
│   │   ├── elevation.py
│   │   ├── satellite.py
│   │   ├── precipitation.py
│   │   ├── gibs.py
│   │   ├── lhasa.py
│   │   ├── bhuvan.py
│   │   ├── ndem.py
│   │   ├── osm.py
│   │   ├── risk.py                  # Main risk calculation endpoint
│   │   ├── zones.py                 # Micro-zone endpoints
│   │   ├── simulation.py            # What-if simulator endpoint
│   │   ├── copilot.py               # AI Copilot endpoint
│   │   ├── trends.py                # Risk trends endpoint
│   │   ├── vulnerable.py            # Vulnerable locations endpoint
│   │   ├── priority.py              # Priority classification endpoint
│   │   ├── response_plan.py         # Response recommendations endpoint
│   │   ├── analysis.py              # Multi-source analysis endpoint
│   │   └── health.py                # Health check endpoint
│   ├── services/                    # Data source integrations
│   │   ├── base.py                  # Base service class (HTTP, cache)
│   │   ├── geocoding_service.py     # Open-Meteo Geocoding
│   │   ├── weather_service.py       # Open-Meteo Weather
│   │   ├── elevation_service.py     # Open-Meteo Elevation
│   │   ├── sentinel_service.py      # Copernicus Sentinel NDVI
│   │   ├── stac_service.py          # Copernicus STAC API
│   │   ├── gpm_service.py           # NASA GPM IMERG Precipitation
│   │   ├── gibs_service.py          # NASA GIBS Visualization
│   │   ├── lhasa_service.py         # NASA LHASA Reference Hazard
│   │   ├── bhuvan_service.py        # ISRO Bhuvan Hazard
│   │   ├── ndem_service.py          # ISRO NDEM Disaster Data
│   │   ├── osm_service.py           # OpenStreetMap Context
│   │   └── notification_service.py  # Firebase Cloud Messaging
│   └── ml/                          # Original ML pipeline (preserved)
│       ├── susceptibility.py
│       ├── synthetic_data.py
│       └── train.py
```

### Frontend (React/Vite)

**File structure:**
```
landslide siet/frontend/
├── package.json                     # Dependencies
├── vite.config.js                   # Vite config
├── index.html                       # Entry HTML
└── src/
    ├── main.jsx                     # React entry
    ├── App.jsx                      # Main app component
    └── styles.css                   # Responsive dashboard styling
```

**Components in App.jsx:**
- Risk Score Card (primary, with border color by level)
- Weather Stats (rainfall, moisture, slope)
- Micro-Zone Map (Leaflet with 4 interactive zones)
- Zone Detail Panel (click zone to see details)
- Explainable Risk Breakdown (factor percentages + explanation)
- What-If Simulator (rainfall/moisture/slope sliders)
- Risk Trend Chart (Recharts area chart)
- Smart Alert Box (CRITICAL/HIGH/MODERATE/LOW)
- AI Copilot Chat Panel (rule-based QA)
- Alert History Table (past alerts with timestamps)

---

## API Endpoints

### Core Risk Assessment
```
GET /api/risk?lat={lat}&lon={lon}
```
Returns:
```json
{
  "location": {"name": "Ooty", "lat": 11.4064, "lon": 76.6932},
  "riskScore": 87,
  "riskLevel": "CRITICAL",
  "factors": ["Heavy rainfall", "High soil moisture", "High slope"],
  "weather": {"temperature_c": 18.5, "humidity": 83, "rain_24h_mm": 64.4},
  "terrain": {"elevation_m": 2240, "slope_deg": 31.2},
  "satellite": {"ndvi": 0.46, "vegetation": "moderate"},
  "historical": {"historical_landslides_nearby": 4},
  "riskExplanation": {...},
  "alert": {...},
  "source_status": {...},
  "updatedAt": "2026-10-05T12:00:00Z",
  "demoMode": true
}
```

### Zones
```
GET /api/zones
GET /api/zones/{zone_name}
```

### Simulation
```
POST /api/simulation?zone=Ooty&rainfall=150&soil_moisture=75&slope=35
```

### AI Copilot
```
GET /api/copilot?question=Which%20zones%20are%20critical?
```

### Trends
```
GET /api/trends
```

### Vulnerable Locations
```
GET /api/vulnerable-locations
```

### Priority & Response
```
GET /api/priority
GET /api/response-plan
```

---

## Installation & Setup

### Local Development

#### 1. Clone the repository
```bash
git clone https://github.com/gnanesh20may-eng/landslide.git
cd landslide
git checkout psa04-integration
```

#### 2. Backend Setup
```bash
cd "landslide siet"
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .\venv\Scripts\Activate.ps1  # Windows PowerShell

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### 3. Create .env file
```bash
cp .env.example .env
# Edit .env as needed (default DEMO_MODE=true)
```

#### 4. Run Backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://127.0.0.1:8000**

API docs: **http://127.0.0.1:8000/docs**

#### 5. Frontend Setup (new terminal)
```bash
cd "landslide siet/frontend"
npm install
npm run dev -- --host 0.0.0.0
```

Frontend will be available at: **http://127.0.0.1:5173**

---

### Docker Deployment

```bash
cd "landslide siet"
docker compose up --build
```

Services will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173

---

## Demo Data

The system comes with 5 pre-configured demo zones:

| Zone | Location | Risk | Rainfall | Moisture | Slope | Incidents |
|------|----------|------|----------|----------|-------|----------|
| A | Wayanad, Kerala | 87 CRITICAL | 142 mm | 78% | 31° | 7 |
| B | Nilgiris, TN | 52 MODERATE | 74 mm | 62% | 26° | 4 |
| C | Darjeeling, WB | 81 CRITICAL | 160 mm | 80% | 34° | 8 |
| D | Kodaikanal, TN | 33 LOW | 48 mm | 54% | 20° | 2 |

**To enable real API data:**
1. Create OAuth credentials for Copernicus, NASA Earthdata, etc.
2. Add credentials to `.env`
3. Set `DEMO_MODE=false`

---

## Risk Calculation Logic

### Weighted Risk Score (0-100)

**Factors:**
```
Base Score: 30

+ Rainfall Component (max 35%)
  - 60+ mm → +22 points
  - 25-60 mm → +10 points

+ Soil Moisture (max 25%)
  - 65%+ → +15 points

+ Slope (max 20%)
  - 25°+ → +16 points
  - 15-25° → +8 points

+ Vegetation/NDVI (max 15%)
  - <0.45 → +10 points (low stability)
  - 0.45-0.6 → +5 points

+ Historical Density (max 18%)
  - 4+ incidents nearby → +18 points
  - 1-3 incidents → +8 points
```

**Classification:**
- 0-30: LOW
- 31-60: MODERATE
- 61-80: HIGH
- 81-100: CRITICAL

### Alert Confidence
```
Confidence = (Supporting Factors / 5) × 100

Example:
- Heavy rainfall + high moisture + steep slope + low vegetation + historical incidents
  = 5 factors aligned
  = 100% confidence → CRITICAL alert

- Only heavy rainfall
  = 1 factor
  = 20% confidence → Monitor only
```

---

## Important Scientific Rules

### What We DO Say:
✅ "AI-based risk estimation"
✅ "Early-warning decision support"
✅ "Prototype prediction"
✅ "AI-generated decision-support alert. This prototype does not replace official disaster-management warnings."

### What We DON'T Say:
❌ "100% accuracy"
❌ "Guaranteed landslide prediction"
❌ "Official government warning"
❌ "Officially deployed system"

### Data Transparency:
- All data sources are labeled:
  - 🟢 LIVE DATA (connected)
  - 🟡 CACHED/DEMO DATA (simulated)
  - 🔴 TEMPORARILY UNAVAILABLE (fallback)
- Never present simulated data as real-time sensor data

---

## Testing

### Backend Tests
```bash
cd "landslide siet"
pytest backend/tests/
```

### API Manual Testing
```bash
# Get risk for a location
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932"

# Get zones
curl http://127.0.0.1:8000/api/zones

# Run simulation
curl -X POST "http://127.0.0.1:8000/api/simulation?zone=Ooty&rainfall=180&soil_moisture=80&slope=35"

# Ask Copilot
curl "http://127.0.0.1:8000/api/copilot?question=Which%20zones%20are%20critical"

# View API docs
open http://127.0.0.1:8000/docs
```

---

## Troubleshooting

### Backend won't start
```
Error: ModuleNotFoundError: No module named 'backend'
```
**Fix:** Ensure you're in the `landslide siet` directory and `PYTHONPATH` is set correctly:
```bash
cd "landslide siet"
export PYTHONPATH=.
uvicorn backend.main:app --reload
```

### Frontend can't connect to backend
```
Error: Failed to fetch http://127.0.0.1:8000/api/risk
```
**Fix:** Ensure backend is running on port 8000 and CORS is enabled (it is by default).

### DEMO_MODE not working
```
Error: API returns "temporarily unavailable"
```
**Fix:** Check `.env` file:
```bash
DEMO_MODE=true
```

---

## Future Enhancements

- [ ] Real-time satellite data integration (Sentinel Hub OAuth)
- [ ] Historical GIS database of past landslides
- [ ] Machine learning model training on historical events
- [ ] Integration with National Disaster Management Authority (NDMA)
- [ ] Mobile app (React Native)
- [ ] SMS/WhatsApp alert notifications
- [ ] Multi-language support (Hindi, Kannada, Telugu)
- [ ] Advanced GIS routing (safe evacuation routes)
- [ ] Crowd-sourced incident reporting

---

## License

This project is open-source and available under the MIT License.

---

## Authors

- **Kalkishree006** - Initial development
- **LandSense Contributors**

---

## Disclaimer

**⚠️ IMPORTANT:**

This is a **prototype system for educational and demonstration purposes only**. It is NOT an official landslide prediction system and does NOT replace government or meteorological agency warnings.

The AI-based risk scores are estimates for decision support. Users must always consult official disaster management authorities for critical decisions.

**Use at your own risk.**

---

**Last Updated:** October 5, 2026
