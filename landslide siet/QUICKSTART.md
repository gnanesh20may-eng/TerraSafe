# Quick Start Guide - LandSense

## 5-Minute Setup

### 1. Clone & Enter Directory
```bash
git clone https://github.com/gnanesh20may-eng/landslide.git
cd landslide
git checkout psa04-integration
cd "landslide siet"
```

### 2. Backend (Terminal 1)
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\venv\Scripts\Activate.ps1  # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload
```

✅ Backend ready at: **http://127.0.0.1:8000**

### 3. Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

✅ Frontend ready at: **http://127.0.0.1:5173**

### 4. Open Browser
```
http://127.0.0.1:5173
```

---

## What You'll See

- 🎯 **Risk Score:** Current landslide risk (0-100)
- 🗺️ **Interactive Map:** 4 zones with live risk colors
- 📊 **What-If Simulator:** Adjust rainfall and watch risk update
- 📈 **Risk Trend:** Historical risk progression (6am-6pm)
- 🤖 **AI Copilot:** Ask questions about zones and risk
- ⚠️ **Smart Alerts:** Automatic warnings at thresholds
- 📋 **Alert History:** Track all past alerts

---

## Test Cases

### Test 1: View Zone Details
1. Click red Zone A marker on map
2. Panel shows: Zone name, risk 87/100, factors, recommendations

### Test 2: Simulate Heavy Rainfall
1. Drag "Rainfall" slider to 200 mm
2. Watch risk increase in real-time
3. Alert changes from MODERATE to CRITICAL

### Test 3: Ask Copilot
1. Type: "Which zones are critical?"
2. Copilot responds with current data

### Test 4: Check Vulnerable Locations
1. Look at data sources panel
2. See Priority 1/2/3 locations near zones

---

## API Endpoints (for testing)

```bash
# Get risk for a location
curl "http://127.0.0.1:8000/api/risk?lat=11.4064&lon=76.6932"

# Simulate rainfall change
curl -X POST "http://127.0.0.1:8000/api/simulation?zone=Ooty&rainfall=180"

# Ask AI
curl "http://127.0.0.1:8000/api/copilot?question=Why%20is%20zone%20A%20dangerous"

# View all zones
curl http://127.0.0.1:8000/api/zones

# Get trends
curl http://127.0.0.1:8000/api/trends

# API docs
open http://127.0.0.1:8000/docs
```

---

## Common Issues & Fixes

### ❌ "ModuleNotFoundError: No module named 'backend'"
```bash
cd "landslide siet"
export PYTHONPATH=.
uvicorn backend.main:app --reload
```

### ❌ "Address already in use"
```bash
# Use a different port
uvicorn backend.main:app --port 8001
```

### ❌ "Cannot GET /api/risk"
- Ensure backend is running on http://127.0.0.1:8000
- Check frontend DevTools → Network → Errors

### ❌ "npm install fails"
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## Next Steps

1. **Run Full Validation:** See `VALIDATION_CHECKLIST.md`
2. **Deploy with Docker:** `docker compose up --build`
3. **Add Real APIs:** Edit `.env` with credentials, set `DEMO_MODE=false`
4. **Read Full Docs:** See `README.md`

---

**Ready to go! 🚀**
