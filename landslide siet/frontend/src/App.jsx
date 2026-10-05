import { Activity, AlertTriangle, Gauge, MapPinned, ShieldAlert, TrendingUp } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Circle, CircleMarker, LayerGroup, LayersControl, MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import { useEffect, useMemo, useState } from 'react'

const zoneData = [
  { name: 'Zone A, Wayanad', lat: 11.6854, lon: 76.1321, risk: 87, level: 'CRITICAL', rainfall: 142, moisture: 78, slope: 31 },
  { name: 'Zone B, Nilgiris', lat: 11.4064, lon: 76.6932, risk: 52, level: 'MODERATE', rainfall: 74, moisture: 62, slope: 26 },
  { name: 'Zone C, Darjeeling', lat: 27.041, lon: 88.2663, risk: 81, level: 'CRITICAL', rainfall: 160, moisture: 80, slope: 34 },
  { name: 'Zone D, Kodaikanal', lat: 10.2381, lon: 77.4892, risk: 33, level: 'LOW', rainfall: 48, moisture: 54, slope: 20 },
]

const trend = [
  { time: '06:00', risk: 32 },
  { time: '09:00', risk: 41 },
  { time: '12:00', risk: 58 },
  { time: '15:00', risk: 74 },
  { time: '18:00', risk: 87 },
]

function getRiskColor(level) {
  return {
    LOW: '#22c55e',
    MODERATE: '#facc15',
    HIGH: '#f97316',
    CRITICAL: '#ef4444',
  }[level] || '#94a3b8'
}

export default function App() {
  const [selectedZone, setSelectedZone] = useState(zoneData[0])
  const [rainfall, setRainfall] = useState(120)
  const [soilMoisture, setSoilMoisture] = useState(72)
  const [slope, setSlope] = useState(30)
  const [riskScore, setRiskScore] = useState(87)
  const [language, setLanguage] = useState('EN')
  const [copilotInput, setCopilotInput] = useState('Which zones are currently critical?')
  const [copilotResponse, setCopilotResponse] = useState('Zone A and Zone C are currently critical. The main drivers are rainfall, soil moisture, and slope.')
  const [alertHistory, setAlertHistory] = useState([
    { time: '2026-10-05 06:00', zone: 'Zone A', level: 'HIGH', reason: 'Heavy rainfall + steep slope' },
    { time: '2026-10-05 12:00', zone: 'Zone C', level: 'CRITICAL', reason: 'Extreme rainfall + saturated soil' },
  ])

  const riskLevel = useMemo(() => {
    if (riskScore <= 30) return 'LOW'
    if (riskScore <= 60) return 'MODERATE'
    if (riskScore <= 80) return 'HIGH'
    return 'CRITICAL'
  }, [riskScore])

  useEffect(() => {
    const base = 30
    const score = Math.min(100, Math.round(base + rainfall / 2.5 + soilMoisture / 2.8 + slope / 1.8))
    setRiskScore(score)
  }, [rainfall, soilMoisture, slope])

  const handleSimulate = () => {
    const newRisk = Math.min(100, Math.round(30 + rainfall / 2.5 + soilMoisture / 2.8 + slope / 1.8))
    setRiskScore(newRisk)
    setAlertHistory((prev) => [
      { time: new Date().toLocaleString(), zone: selectedZone.name, level: newRisk >= 81 ? 'CRITICAL' : newRisk >= 61 ? 'HIGH' : 'MODERATE', reason: 'Simulated rainfall scenario' },
      ...prev,
    ])
  }

  const askCopilot = () => {
    if (copilotInput.toLowerCase().includes('critical')) {
      setCopilotResponse('Zone A and Zone C are critical based on rainfall, slope, and soil moisture. The system recommends immediate inspection.')
    } else if (copilotInput.toLowerCase().includes('rainfall')) {
      setCopilotResponse('If rainfall increases to 180 mm, the estimated risk rises sharply in the most affected zones, especially Wayanad and Darjeeling.')
    } else {
      setCopilotResponse('The safest current area is Zone D, based on lower rainfall and a moderate slope profile.')
    }
  }

  return (
    <div className="app-shell">
      <header className="header">
        <div>
          <p className="eyebrow">Explainable AI Landslide Decision Support</p>
          <h1>LandSense</h1>
        </div>
        <div className="header-actions">
          <button className="secondary">DEMO MODE</button>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="EN">English</option>
            <option value="TA">தமிழ்</option>
          </select>
        </div>
      </header>

      <section className="summary-grid">
        <div className="card primary" style={{ borderColor: getRiskColor(riskLevel) }}>
          <div className="card-head"><Gauge size={18} /> Risk Score</div>
          <div className="big-number">{riskScore}/100</div>
          <div className="badge" style={{ background: getRiskColor(riskLevel) }}>{riskLevel}</div>
          <small>AI-based risk estimation</small>
        </div>

        <div className="card">
          <div className="card-head"><Activity size={18} /> Rainfall</div>
          <div className="metric">{rainfall} mm</div>
          <small>24h precipitation</small>
        </div>

        <div className="card">
          <div className="card-head"><ShieldAlert size={18} /> Soil Moisture</div>
          <div className="metric">{soilMoisture}%</div>
          <small>surface saturation</small>
        </div>

        <div className="card">
          <div className="card-head"><TrendingUp size={18} /> Slope</div>
          <div className="metric">{slope}°</div>
          <small>terrain steepness</small>
        </div>
      </section>

      <section className="content-grid">
        <div className="panel span-2">
          <div className="panel-header">
            <h3>Micro-Zone Risk Map</h3>
            <span className="note">LIVE / SIMULATED / HISTORICAL</span>
          </div>
          <MapContainer center={[11.4, 76.6]} zoom={6} className="map-box">
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
            <LayersControl position="topright">
              {zoneData.map((zone) => (
                <LayersControl.Overlay checked key={zone.name} name={zone.name}>
                  <LayerGroup>
                    <CircleMarker center={[zone.lat, zone.lon]} radius={16} pathOptions={{ color: getRiskColor(zone.level), fillColor: getRiskColor(zone.level), fillOpacity: 0.9 }} eventHandlers={{ click: () => setSelectedZone(zone) }} />
                  </LayerGroup>
                </LayersControl.Overlay>
              ))}
            </LayersControl>
          </MapContainer>
        </div>

        <aside className="panel">
          <div className="panel-header">
            <h3>Zone Detail</h3>
          </div>
          <div className="zone-detail">
            <h4>{selectedZone.name}</h4>
            <div className="badge large" style={{ background: getRiskColor(selectedZone.level) }}>{selectedZone.level}</div>
            <ul>
              <li>Risk: {selectedZone.risk}/100</li>
              <li>Rainfall: {selectedZone.rainfall} mm</li>
              <li>Soil moisture: {selectedZone.moisture}%</li>
              <li>Slope: {selectedZone.slope}°</li>
              <li>Historical incidents: {selectedZone.risk >= 80 ? 7 : 4}</li>
            </ul>
            <p>Why is this zone at risk? Heavy rainfall, saturated soil, and steep slopes combine to create high exposure.</p>
            <p><strong>Recommended action:</strong> Inspect road cut slopes and prepare evacuation measures for vulnerable settlements.</p>
          </div>
        </aside>
      </section>

      <section className="second-grid">
        <div className="panel">
          <div className="panel-header">
            <h3>Explainable AI Risk Breakdown</h3>
          </div>
          <div className="risk-bars">
            {[
              ['Rainfall', 35],
              ['Soil Moisture', 25],
              ['Slope', 20],
              ['History', 12],
              ['Vegetation', 8],
            ].map(([label, value]) => (
              <div key={label} className="bar-row">
                <span>{label}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${value}%` }} />
                </div>
                <strong>{value}%</strong>
              </div>
            ))}
          </div>
          <div className="explanation-box">
            <strong>Why is this zone at risk?</strong>
            <p>Heavy rainfall, high soil saturation, and steep terrain create an elevated likelihood of shallow landslides and slope failures.</p>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3>What-if Rainfall Simulator</h3>
          </div>
          <div className="slider-group">
            <label>Rainfall: {rainfall} mm</label>
            <input type="range" min="20" max="220" value={rainfall} onChange={(e) => setRainfall(Number(e.target.value))} />
            <label>Soil Moisture: {soilMoisture}%</label>
            <input type="range" min="20" max="95" value={soilMoisture} onChange={(e) => setSoilMoisture(Number(e.target.value))} />
            <label>Slope: {slope}°</label>
            <input type="range" min="5" max="60" value={slope} onChange={(e) => setSlope(Number(e.target.value))} />
          </div>
          <button className="primary-btn" onClick={handleSimulate}>Simulate Heavy Rainfall</button>
          <div className="sim-result">
            <strong>Estimated risk:</strong> {riskScore}/100 ({riskLevel})
          </div>
        </div>
      </section>

      <section className="chart-panel panel">
        <div className="panel-header">
          <h3>Risk Trend</h3>
          <span>current vs predicted</span>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={trend}>
            <defs>
              <linearGradient id="fillRisk" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#cbd5e1" />
            <YAxis stroke="#cbd5e1" />
            <Tooltip />
            <Area type="monotone" dataKey="risk" stroke="#ef4444" fill="url(#fillRisk)" />
          </AreaChart>
        </ResponsiveContainer>
      </section>

      <section className="bottom-grid">
        <div className="panel">
          <div className="panel-header">
            <h3>Smart Early Warning</h3>
          </div>
          <div className="alert-box" style={{ borderColor: getRiskColor(riskLevel) }}>
            <strong>CRITICAL LANDSLIDE WARNING</strong>
            <p>Zone: {selectedZone.name}</p>
            <p>Risk: {riskScore}/100</p>
            <p>Main reasons: Heavy rainfall, high soil moisture, steep terrain</p>
            <p>Recommended action: Inspect vulnerable locations and prepare evacuation measures.</p>
            <small>Alert timestamp: 2026-10-05T12:00:00Z | Status: active</small>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3>Landsafe Copilot</h3>
          </div>
          <div className="copilot-box">
            <input
              value={copilotInput}
              onChange={(e) => setCopilotInput(e.target.value)}
              placeholder="Ask about critical zones..."
            />
            <button className="primary-btn" onClick={askCopilot}>Ask</button>
            <div className="copilot-answer">{copilotResponse}</div>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h3>Alert History</h3>
        </div>
        <div className="history-list">
          {alertHistory.map((item, idx) => (
            <div key={`${item.time}-${idx}`} className="history-item">
              <span>{item.time}</span>
              <strong>{item.zone}</strong>
              <span className="small-badge" style={{ background: getRiskColor(item.level) }}>{item.level}</span>
              <span>{item.reason}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
