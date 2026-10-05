# Troubleshooting Guide - LandSense

## Backend Issues

### Issue: Backend won't start

#### Error: `ModuleNotFoundError: No module named 'backend'`

**Cause:** Python path not configured correctly.

**Fix:**
```bash
cd "landslide siet"
export PYTHONPATH=.
uvicorn backend.main:app --reload
```

Or on Windows (PowerShell):
```powershell
cd "landslide siet"
$env:PYTHONPATH="."
uvicorn backend.main:app --reload
```

---

#### Error: `address already in use`

**Cause:** Port 8000 is already in use.

**Fix (Option 1):** Kill existing process
```bash
lsof -i :8000
kill -9 <PID>
```

**Fix (Option 2):** Use different port
```bash
uvicorn backend.main:app --port 8001
```

Then update frontend proxy in `vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8001',  // Changed port
    changeOrigin: true,
  }
}
```

---

#### Error: `ImportError` in routes

**Cause:** Route files don't exist or have wrong paths.

**Fix:** Verify all files exist
```bash
ls backend/app/routes/
ls backend/app/services/
```

Expected files:
```
routes/:
  geocode.py
  weather.py
  elevation.py
  satellite.py
  precipitation.py
  gibs.py
  lhasa.py
  bhuvan.py
  ndem.py
  osm.py
  risk.py
  zones.py
  simulation.py
  copilot.py
  trends.py
  vulnerable.py
  priority.py
  response_plan.py
  analysis.py
  health.py

services/:
  base.py
  geocoding_service.py
  weather_service.py
  elevation_service.py
  sentinel_service.py
  stac_service.py
  gpm_service.py
  gibs_service.py
  lhasa_service.py
  bhuvan_service.py
  ndem_service.py
  osm_service.py
  notification_service.py
```

If files are missing, re-clone or re-download from GitHub.

---

#### Error: `No module named 'httpx'` or other packages

**Cause:** Dependencies not installed.

**Fix:**
```bash
pip install -r requirements.txt
```

Or install specific package:
```bash
pip install httpx
pip install firebase-admin
```

---

### Issue: API returns error responses

#### Error: 404 Not Found on `/api/risk`

**Cause:** Route not registered in `main.py`.

**Fix:** Check `backend/main.py` includes all routers
```python
from backend.app.routes.risk import router as risk_router
app.include_router(risk_router)
```

---

#### Error: 500 Internal Server Error

**Cause:** Runtime error in route handler.

**Fix:** Check server logs
```
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  ...
```

Common causes:
- Missing `.env` file → `cp .env.example .env`
- Wrong config value → Check `backend/app/config.py`
- Missing demo data → Check `backend/app/demo_data.py`

---

#### Error: CORS error from frontend

**Error:**
```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/api/risk' 
from origin 'http://127.0.0.1:5173' has been blocked by CORS policy
```

**Fix:** Ensure CORS middleware in `backend/main.py`
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Frontend Issues

### Issue: Frontend won't start

#### Error: `npm ERR! Cannot find module`

**Cause:** Dependencies not installed.

**Fix:**
```bash
cd frontend
npm install
```

---

#### Error: `Port 5173 already in use`

**Cause:** Another process using port 5173.

**Fix (Option 1):** Kill existing process
```bash
lsof -i :5173
kill -9 <PID>
```

**Fix (Option 2):** Use different port
```bash
npm run dev -- --port 5174
```

---

#### Error: Vite compilation fails

**Error:**
```
[plugin:vite:vue] ...
Parse error ...
```

**Fix:** Check syntax in `.jsx` files
```bash
# Validate JSX
cat frontend/src/App.jsx | head -20
```

---

### Issue: Frontend loads but doesn't work

#### Problem: White screen on load

**Cause:** React app not rendering.

**Fix:** Open DevTools (F12) → Console → Check for errors

Common issues:
- Missing root div: Check `index.html` has `<div id="root"></div>`
- Syntax error in App.jsx: Check for missing commas, parentheses
- Missing CSS: Check `styles.css` is imported in `main.jsx`

---

#### Problem: Map doesn't render

**Cause:** Leaflet CSS not loaded.

**Fix:** Check `index.html`
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

Should be before `<script type="module" src="/src/main.jsx"></script>`

---

#### Problem: Sliders don't work

**Cause:** React state not updating.

**Fix:** Check `App.jsx` has state handlers:
```javascript
const [rainfall, setRainfall] = useState(120)
const handleRainfallChange = (value) => setRainfall(value)
```

---

#### Problem: API calls fail

**Error in console:**
```
Failed to fetch http://127.0.0.1:8000/api/risk
```

**Fix:**
1. Ensure backend is running: `curl http://127.0.0.1:8000/health`
2. Check proxy in `vite.config.js` points to correct backend port
3. Verify CORS is enabled on backend
4. Check frontend Network tab for actual error

---

### Issue: Frontend looks broken

#### Problem: Styling is missing

**Cause:** CSS file not loaded.

**Fix:** Check import in `main.jsx`
```javascript
import './styles.css'
```

---

#### Problem: Dark theme doesn't load

**Cause:** CSS not applied.

**Fix:** Check `styles.css` has body styling
```css
body {
  background: #07111f;
  color: #e2e8f0;
}
```

---

#### Problem: Icons don't appear

**Cause:** lucide-react not installed.

**Fix:**
```bash
cd frontend
npm install lucide-react
```

---

## Frontend-Backend Communication Issues

### Problem: Frontend can't reach backend

**Scenario:** Frontend loads but no data displays.

**Debug steps:**
1. Open DevTools → Network tab
2. Reload page
3. Look for `/api/...` requests
4. Check response status and body

**If requests don't appear:**
- Backend not running → Start it: `uvicorn backend.main:app --reload`
- Proxy not configured → Check `vite.config.js`
- Wrong port → Verify backend is on 8000, frontend on 5173

**If requests return 404:**
- Route not registered in backend → Check `backend/main.py`
- Wrong route path → Compare with API docs at `/docs`

**If requests return 500:**
- Backend error → Check server logs
- Missing .env file → `cp .env.example .env`
- Demo data issue → Check `backend/app/demo_data.py`

---

## Docker Issues

### Problem: `docker compose up` fails

#### Error: `Cannot connect to Docker daemon`

**Fix:** Start Docker service
```bash
# macOS
open /Applications/Docker.app

# Linux
sudo systemctl start docker

# Windows
# Start Docker Desktop from Start Menu
```

---

#### Error: `failed to build image`

**Cause:** Dockerfile error or file not found.

**Fix:** Verify files exist
```bash
ls Dockerfile
ls Dockerfile.frontend
ls requirements.txt
ls frontend/package.json
```

---

#### Error: Port conflict

**Error:**
```
Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:8000
```

**Fix:**
```bash
# Option 1: Stop other containers
docker compose down

# Option 2: Use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Frontend calls :8001
  - "5174:5173"
```

---

## Data & Logic Issues

### Problem: Risk score doesn't change

**Scenario:** Move sliders but risk stays 87.

**Fix:** Check React state in App.jsx
```javascript
// Should update on slider change
const [rainfall, setRainfall] = useState(120)

// Effect should recalculate risk
useEffect(() => {
  const score = Math.round(30 + rainfall / 2.5 + ...)
  setRiskScore(score)
}, [rainfall, soilMoisture, slope])
```

---

### Problem: Copilot returns generic answer

**Scenario:** Ask "Which zones are critical?" but get "I can answer questions..."

**Fix:** Check `backend/app/routes/copilot.py` has logic for that question
```python
if "critical" in q and "zones" in q:
    return {"answer": "Zone A and Zone C are currently critical..."}
```

---

### Problem: Demo data not showing

**Scenario:** API returns `temporarily unavailable`.

**Fix:** Check DEMO_MODE in `.env`
```bash
cat .env | grep DEMO_MODE
# Should output: DEMO_MODE=true
```

If not set correctly:
```bash
echo "DEMO_MODE=true" >> .env
```

Then restart backend.

---

## Performance Issues

### Problem: Dashboard is slow

#### Frontend slow

**Check:** DevTools → Performance tab

**If slow load time:**
- Reduce bundle size: Check unused imports
- Enable production build: `npm run build`
- Check for console errors that block rendering

**If slow interactions:**
- Avoid unnecessary re-renders: Check `useEffect` dependencies
- Use React DevTools Profiler: Identify slow components

#### Backend slow

**Check:** Response time
```bash
time curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932"
```

**If > 1 second:**
- Enable caching: Check `backend/app/cache.py` TTL
- Check demo data loads quickly: Test with `curl -v`
- Check for slow external API calls (shouldn't happen in DEMO_MODE)

---

## Getting Help

### Check Logs

**Backend logs:**
```bash
# Shows all requests and errors
uvicorn backend.main:app --reload --log-level debug
```

**Frontend logs:**
```bash
# Open DevTools → Console
# F12 in browser
```

### Test Individual Components

```bash
# Test backend health
curl http://127.0.0.1:8000/health

# Test risk API
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932" | jq .

# Test zones
curl http://127.0.0.1:8000/api/zones | jq .

# Test simulation
curl -X POST "http://127.0.0.1:8000/api/simulation?zone=Ooty&rainfall=150" | jq .
```

### Check File Permissions

```bash
# Ensure all files are readable
ls -la backend/app/
ls -la frontend/src/
```

---

## Still Having Issues?

1. **Re-read the VALIDATION_CHECKLIST.md** - Most issues have solutions there
2. **Check GitHub Issues** - Similar problems might be documented
3. **Review Code Comments** - Check docstrings in Python files
4. **Test in isolation** - Test backend and frontend separately
5. **Clean install** - Delete `node_modules`, `venv`, run fresh install

---

**Last Updated:** October 5, 2026
