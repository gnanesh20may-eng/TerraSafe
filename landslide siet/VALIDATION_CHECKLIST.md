# LOCAL VALIDATION CHECKLIST FOR LANDSENSE PSA 04

## Pre-Flight Checks

### 1. Environment Setup
- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed
- [ ] Git configured
- [ ] Repository cloned to `landslide siet/`

### 2. Directory Structure Verification
```bash
ls -la "landslide siet/"
# Should show:
# backend/
# frontend/
# .env.example
# requirements.txt
# README.md
# docker-compose.yml
```

---

## Backend Validation (Python/FastAPI)

### Step 1: Virtual Environment
```bash
cd "landslide siet"
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .\venv\Scripts\Activate.ps1  # Windows PowerShell
```
- [ ] Virtual environment created
- [ ] Prompt shows `(.venv)`

### Step 2: Install Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
- [ ] All packages installed without errors
- [ ] Check key packages:
  ```bash
  python -c "import fastapi; import httpx; import pydantic; print('OK')"
  ```
- [ ] Output should be: `OK`

### Step 3: Create .env File
```bash
cp .env.example .env
```
- [ ] `.env` file created
- [ ] Verify content:
  ```bash
  cat .env | grep DEMO_MODE
  # Should output: DEMO_MODE=true
  ```

### Step 4: Test Backend Startup
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

- [ ] Backend starts without errors
- [ ] No import errors
- [ ] No module not found errors
- [ ] Server is ready

### Step 5: Backend Health Check (new terminal)
```bash
curl http://127.0.0.1:8000/health
```

**Expected response:**
```json
{"status": "ok"}
```

- [ ] Health endpoint returns 200
- [ ] Response body is valid JSON

### Step 6: Test Main Risk API
```bash
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932"
```

**Expected response (partial):**
```json
{
  "location": {"name": "Ooty", "lat": 11.4064, "lon": 76.6932},
  "riskScore": 87,
  "riskLevel": "CRITICAL",
  "factors": ["Heavy rainfall", "High soil moisture", "High slope"],
  "demoMode": true,
  "updatedAt": "..."
}
```

- [ ] API returns 200 status
- [ ] Response includes `riskScore` (0-100)
- [ ] Response includes `riskLevel` (LOW/MODERATE/HIGH/CRITICAL)
- [ ] Response includes `factors` array
- [ ] Response includes `demoMode: true`

### Step 7: Test Other Key Endpoints

#### Zones Endpoint
```bash
curl http://127.0.0.1:8000/api/zones
```
- [ ] Returns list of 4 zones
- [ ] Each zone has `name`, `risk_score`, `risk_level`

#### Simulation Endpoint
```bash
curl -X POST "http://127.0.0.1:8000/api/simulation?zone=Ooty&rainfall=150&soil_moisture=75&slope=35"
```
- [ ] Returns 200
- [ ] Response includes `current` (simulated risk score)
- [ ] Response includes `risk_level`

#### Copilot Endpoint
```bash
curl "http://127.0.0.1:8000/api/copilot?question=Which%20zones%20are%20critical"
```
- [ ] Returns 200
- [ ] Response includes `answer` field
- [ ] Answer uses application data (not invented)

#### Trends Endpoint
```bash
curl http://127.0.0.1:8000/api/trends
```
- [ ] Returns 200
- [ ] Response includes `trend` array with time-series data
- [ ] Response includes `current` risk value

#### Vulnerable Locations
```bash
curl http://127.0.0.1:8000/api/vulnerable-locations
```
- [ ] Returns 200
- [ ] Response includes vulnerable locations and priorities

### Step 8: API Documentation
```bash
open http://127.0.0.1:8000/docs
```

- [ ] Swagger UI loads
- [ ] All endpoints listed:
  - GET /api/risk
  - GET /api/zones
  - POST /api/simulation
  - GET /api/copilot
  - GET /api/trends
  - GET /api/vulnerable-locations
  - GET /api/priority
  - GET /api/response-plan
  - GET /api/geocode
  - GET /api/weather
  - GET /api/elevation
  - GET /api/satellite
  - GET /api/precipitation
  - And more...

---

## Frontend Validation (React/Vite)

### Step 1: Navigate to Frontend
```bash
cd "landslide siet/frontend"
pwd  # should show .../landslide siet/frontend
```

- [ ] Directory changed successfully

### Step 2: Install Dependencies
```bash
npm install
```

- [ ] npm install completes without errors
- [ ] `node_modules/` directory created
- [ ] `package-lock.json` generated

### Step 3: Verify Dependencies
```bash
npm list react react-dom vite leaflet recharts lucide-react
```

- [ ] All packages listed with versions
- [ ] No `unmet dependencies` messages

### Step 4: Start Frontend Dev Server
```bash
npm run dev -- --host 0.0.0.0
```

**Expected output:**
```
  VITE v5.4.10  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

- [ ] Vite dev server starts
- [ ] Server is listening on port 5173
- [ ] No compilation errors

### Step 5: Open Frontend in Browser
```bash
open http://127.0.0.1:5173
```

- [ ] Dashboard loads without white screen
- [ ] Header shows: "LandSense" and "DEMO MODE" badge
- [ ] No console errors (check DevTools)

### Step 6: Verify Dashboard Components

#### Risk Score Card
- [ ] Displays number (e.g., "87/100")
- [ ] Shows risk level (e.g., "CRITICAL")
- [ ] Border color matches risk level (red for CRITICAL)
- [ ] Shows "AI-based risk estimation" note

#### Weather Stats
- [ ] Rainfall card shows value (e.g., "120 mm")
- [ ] Soil Moisture shows value (e.g., "72%")
- [ ] Slope shows value (e.g., "30°")

#### Micro-Zone Map
- [ ] Map loads with OpenStreetMap tiles
- [ ] 4 zones visible as colored circle markers
- [ ] Can click zones to view details
- [ ] Layers control shows on top-right

#### Zone Detail Panel
- [ ] Shows selected zone name
- [ ] Displays risk badge
- [ ] Lists: risk score, rainfall, moisture, slope, incidents
- [ ] Shows explanation: "Why is this zone at risk?"
- [ ] Shows recommended action

#### Explainable AI Breakdown
- [ ] Shows factor contribution bars (Rainfall, Moisture, Slope, History, Vegetation)
- [ ] Each bar shows percentage (sum ~100%)
- [ ] Explanation box appears below
- [ ] Text explains why zone is risky

#### What-If Simulator
- [ ] Rainfall slider works (20-220 mm)
- [ ] Soil Moisture slider works (20-95%)
- [ ] Slope slider works (5-60°)
- [ ] "Simulate Heavy Rainfall" button clickable
- [ ] Risk score updates when sliders change
- [ ] Result box shows "Estimated risk: X/100 (LEVEL)"

#### Risk Trend Chart
- [ ] Area chart displays
- [ ] Shows 5 data points over time (06:00 to 18:00)
- [ ] Current risk is highest point (87)
- [ ] Chart is responsive

#### Smart Alert Box
- [ ] Shows alert level (CRITICAL/HIGH/MODERATE/LOW)
- [ ] Red border for CRITICAL alert
- [ ] Displays zone, risk score, reasons, recommendations
- [ ] Shows timestamp and status
- [ ] Includes disclaimer text

#### AI Copilot Panel
- [ ] Input field for questions
- [ ] "Ask" button
- [ ] Response area shows answers
- [ ] Answers use data from app (e.g., "Zone A and Zone C are critical...")

#### Alert History
- [ ] Table displays past alerts
- [ ] Shows: timestamp, zone, risk level, reason
- [ ] At least 2 historical entries visible

### Step 7: Test Interactivity

#### Change Rainfall
1. Move rainfall slider to 180 mm
2. Check risk score increases
3. Check zone colors update (yellow→orange→red)
4. Check alert message updates
- [ ] All changes reflect in real-time

#### Click Zone on Map
1. Click on yellow Zone B marker
2. Zone detail panel updates
3. Shows Zone B information
4. Risk level changes to MODERATE
- [ ] Zone switching works

#### Ask Copilot
1. Type: "Which zones are critical?"
2. Click Ask
3. Response appears
- [ ] Copilot returns relevant answer using app data

#### Change Language
1. Click language selector (English/Tamil)
2. UI text should attempt to translate
- [ ] Selector works (data structure ready for translations)

### Step 8: Console Check
Open DevTools (F12) → Console tab

- [ ] No red errors
- [ ] No "Failed to fetch" messages (if backend is running)
- [ ] No React warnings about missing keys or props

---

## Frontend-Backend Communication

### Step 1: Verify Proxy Configuration

In `vite.config.js`, confirm:
```javascript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
  }
}
```

- [ ] Config includes `/api` proxy
- [ ] Target is `http://127.0.0.1:8000`

### Step 2: Test API Call from Frontend

Open Browser DevTools (F12) → Network tab:
1. Reload page
2. Filter by "Fetch/XHR"
3. Look for requests to `/api/...*`

- [ ] Requests appear (e.g., `/api/risk`)
- [ ] Status is 200
- [ ] Response shows JSON data

### Step 3: Simulate Heavy Rainfall

1. Move rainfall slider to 200 mm
2. Watch Network tab
3. No API calls needed (simulated locally)
4. Risk score recalculates immediately

- [ ] Simulation works without API calls
- [ ] Risk updates instantly

---

## Error Troubleshooting

### Backend Issues

**Error: `ModuleNotFoundError: No module named 'backend'`**
```bash
# Fix: Ensure PYTHONPATH is set
export PYTHONPATH="."
uvicorn backend.main:app --reload
```

**Error: `ImportError` in routes**
```bash
# Fix: Check file names match imports
ls backend/app/routes/
ls backend/app/services/
# Verify all .py files exist
```

**Error: `Address already in use` on port 8000**
```bash
# Fix: Kill existing process or use different port
lsof -i :8000
kill -9 <PID>
# or
uvicorn backend.main:app --port 8001
```

### Frontend Issues

**Error: `npm ERR! Cannot find module`**
```bash
# Fix: Clean and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: CORS error when calling backend**
```
Access to XMLHttpRequest blocked by CORS policy
```
- [ ] Ensure backend is running on port 8000
- [ ] Confirm CORS middleware is enabled in `backend/main.py`
- [ ] Check proxy in `vite.config.js`

**Error: Map doesn't render**
```bash
# Fix: Ensure leaflet CSS is loaded
# In index.html, check:
# <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

---

## Performance Checks

### Backend Response Time
```bash
time curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932"
```

- [ ] Response time < 500ms
- [ ] Acceptable for real-time dashboard

### Frontend Load Time
1. Open DevTools → Performance tab
2. Click reload
3. Wait for page load complete

- [ ] Initial load < 3 seconds
- [ ] Time to Interactive < 5 seconds

---

## Data Validation

### Risk Score Bounds
```bash
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932" | grep riskScore
```

- [ ] Score is between 0 and 100
- [ ] Score is integer (no decimals)

### Risk Level Classification
For given risk score:
- [ ] 0-30: "LOW"
- [ ] 31-60: "MODERATE"
- [ ] 61-80: "HIGH"
- [ ] 81-100: "CRITICAL"

### Factor Breakdown
```bash
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932" | jq '.riskExplanation.contributing_factors'
```

- [ ] Factors sum to approximately 100%
- [ ] All factors are positive percentages
- [ ] Factors include: Rainfall, Moisture, Slope, History, Vegetation

### Demo Data Consistency
```bash
curl http://127.0.0.1:8000/api/zones | jq '.zones | length'
```

- [ ] Returns 4 (four zones)
- [ ] Each zone has consistent data

---

## Demo Mode Verification

### Check DEMO_MODE is Active
```bash
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932" | grep demoMode
```

- [ ] Output includes: `"demoMode": true`

### Verify Cached Data Labels
```bash
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932" | jq '.source_status'
```

- [ ] Shows sources with status: "connected", "cached", "optional"
- [ ] No source marked as "unavailable" with fake data

### Disclaimer Check
1. Load frontend dashboard
2. Look for disclaimer text

- [ ] Message visible: "AI-generated decision-support alert. This prototype does not replace official disaster-management warnings."

---

## Scientific Rules Compliance

### What System DOES Say
- [ ] "AI-based risk estimation" ✓
- [ ] "Early-warning decision support" ✓
- [ ] "Prototype prediction" ✓
- [ ] Includes disclaimer on alerts ✓
- [ ] Never claims 100% accuracy ✓
- [ ] Never claims official warning ✓
- [ ] Never claims guaranteed prediction ✓

### Data Transparency
- [ ] All data sources labeled (LIVE/CACHED/UNAVAILABLE)
- [ ] No simulated data presented as real-time sensor data
- [ ] Demo mode clearly labeled in UI
- [ ] Alert history shows which data was used

---

## End-to-End Demo Flow

### Scenario: Monitor Wayanad Zone During Heavy Rainfall

**Step 1:** Open Dashboard
```
http://127.0.0.1:5173
```
- [ ] Dashboard loads with Zone A (Wayanad) data
- [ ] Risk shows 87/100 (CRITICAL)

**Step 2:** Review Current Risk
- [ ] Check factors: rainfall (142 mm), moisture (78%), slope (31°)
- [ ] Read explanation: "Heavy rainfall, saturated soil, steep slopes..."
- [ ] Copilot confirms: "Zone A is dangerous because..."

**Step 3:** Run What-If Simulation
- [ ] Change rainfall slider to 200 mm
- [ ] Risk increases to ~95/100 (stays CRITICAL)
- [ ] Alert updates: "CRITICAL LANDSLIDE WARNING"
- [ ] Recommended action: "Inspect vulnerable locations..."

**Step 4:** Check Vulnerable Locations
- [ ] Map shows Zone A selected
- [ ] Nearby resources: School A, Hospital B, Road segment 7
- [ ] All marked as Priority 1 (immediate attention)

**Step 5:** Review Trend
- [ ] Risk chart shows progression: 32 → 41 → 58 → 74 → 87
- [ ] Current peak at 87 (CRITICAL)

**Step 6:** Ask AI Copilot
- [ ] Ask: "What would reduce the risk?"
- [ ] Response: "Risk could fall below critical if rainfall decreases..."
- [ ] Reduce rainfall slider to 80 mm
- [ ] Risk drops to ~45 (MODERATE)
- [ ] Copilot updates recommendation

**Step 7:** Check Alert History
- [ ] Alert log shows:
  - 2026-10-05 06:00 | Zone A | HIGH | Heavy rainfall
  - 2026-10-05 12:00 | Zone C | CRITICAL | Extreme rainfall
  - Simulation | Zone A | CRITICAL | User scenario

- [ ] All alerts logged with source indicated

---

## Final Sign-Off

- [ ] Backend starts without errors
- [ ] All API endpoints respond with 200 status
- [ ] Frontend loads and renders correctly
- [ ] Map displays with 4 interactive zones
- [ ] Risk simulation updates in real-time
- [ ] Copilot responds with data-driven answers
- [ ] Alert system generates appropriate warnings
- [ ] All scientific disclaimers visible
- [ ] Data sources clearly labeled
- [ ] Demo mode active and labeled
- [ ] End-to-end flow works as expected
- [ ] No console errors
- [ ] Response times acceptable (<500ms for API)
- [ ] Mobile responsive (test on different screen sizes)
- [ ] Dark theme loads correctly
- [ ] Color coding matches risk levels

---

## Go-Live Checklist

Before deploying to production:

- [ ] Set `DEMO_MODE=false` in `.env` (when real APIs ready)
- [ ] Add real API credentials to `.env`
- [ ] Review all warning messages and disclaimers
- [ ] Test with real data from one or more sources
- [ ] Verify alert notification system (Firebase)
- [ ] Test multi-user concurrent access
- [ ] Load test: can system handle 100+ concurrent users?
- [ ] Security audit: no API keys in frontend
- [ ] SSL/HTTPS configured
- [ ] Rate limiting enabled
- [ ] Logging and monitoring enabled
- [ ] Backup strategy for historical data
- [ ] Disaster recovery plan documented

---

**Last Updated:** October 5, 2026
**Version:** 1.0.0
**Status:** Ready for Testing ✓
