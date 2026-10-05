import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import toast, { Toaster } from 'react-hot-toast'
import {
  Activity, AlertTriangle, ArrowRight, ArrowUpRight, Bell, Bookmark,
  Check, ChevronDown, CircleHelp, CloudRain, Compass, Flame, Home, Layers, LocateFixed,
  Map as MapIcon, MapPin, Menu, Mountain, Navigation, Plus, Search, Settings as SettingsIcon,
  Shield, ShieldCheck, SlidersHorizontal, Sparkles, Wind, X,
} from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis } from 'recharts'
import TerrainMap from './components/TerrainMap.jsx'
import { areas, getAreaRisk, getRiskCopy, signals, safeZones, timelineData } from './data/mockData.js'
import { getStored, setStored } from './services/appService.js'
import './App.css'
import EmergencyQuickStart from './components/EmergencyQuickStart'

// API URL from Vercel env var (VITE_API_URL=/api/v1 in production)
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const navItems = [
  { to: '/', label: 'Home', icon: Home, end: true },
  { to: '/evaluation', label: 'Evaluation', icon: Activity },
  { to: '/rescue', label: 'Rescue hub', icon: ShieldCheck },
  { to: '/places', label: 'My places', icon: Bookmark },
]

function App() {
  const [selectedArea, setSelectedArea] = useState(() => getStored('terrasafe.area', areas[0]))
  const [savedPlaces, setSavedPlaces] = useState(() => getStored('terrasafe.places', [
    { id: 'home', name: 'Home', area: 'Coimbatore', type: 'Home' },
    { id: 'college', name: 'College', area: 'Ooty', type: 'College' },
  ]))
  const [settings, setSettings] = useState(() => getStored('terrasafe.settings', {
    earlyWarnings: true, locationAlerts: true, terrain3d: true, satellite: false,
    units: 'Metric', theme: 'Light', language: 'English',
  }))

  useEffect(() => { setStored('terrasafe.area', selectedArea) }, [selectedArea])
  useEffect(() => { setStored('terrasafe.places', savedPlaces) }, [savedPlaces])
  useEffect(() => { setStored('terrasafe.settings', settings) }, [settings])
  useEffect(() => {
    const showNotice = (event) => toast(event.detail)
    window.addEventListener('terrasafe-toast', showNotice)
    return () => window.removeEventListener('terrasafe-toast', showNotice)
  }, [])

  return (
    <BrowserRouter>
      <Toaster position="top-right" toastOptions={{ duration: 3500 }} />
      <AppFrame
        selectedArea={selectedArea}
        setSelectedArea={setSelectedArea}
        savedPlaces={savedPlaces}
        setSavedPlaces={setSavedPlaces}
        settings={settings}
        setSettings={setSettings}
      />
    </BrowserRouter>
  )
}

function AppFrame(props) {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pageTitle = navItems.find((item) => item.to === location.pathname)?.label || 'Settings'
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" to="/" aria-label="TerraSafe home">
          <span className="brand-mark"><Mountain size={21} strokeWidth={2.4} /></span>
          <span>terra<span className="brand-light">safe</span><small>ENVIRONMENTAL INTELLIGENCE</small></span>
        </Link>
        <div className="sidebar-label">WORKSPACE</div>
        <nav className="side-nav" aria-label="Main navigation">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Icon size={18} /><span>{label}</span>{label === 'Rescue hub' && <i className="nav-dot" />}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-spacer" />
        <div className="sidebar-note"><span className="note-icon"><Sparkles size={16} /></span><p><strong>Clarity, when it matters.</strong><br />Local signals, made useful.</p></div>
        <NavLink to="/settings" className={({ isActive }) => `nav-link settings-link ${isActive ? 'active' : ''}`}><SettingsIcon size={18} /><span>Settings</span></NavLink>
        <button className="profile-row" type="button" onClick={() => toast('Your profile is up to date.')} aria-label="User profile">
          <span className="avatar">AK</span><span className="profile-copy"><strong>Arun Kumar</strong><small>Personal account</small></span><span className="online-dot" />
        </button>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <div className="mobile-brand"><span className="brand-mark"><Mountain size={19} /></span><strong>terrasafe</strong></div>
          <button className="mobile-menu" aria-label="Open navigation" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}><Menu size={20} /></button>
          <div className="breadcrumb"><span>Workspace</span><span className="crumb-slash">/</span><strong>{pageTitle}</strong></div>
          <div className="topbar-actions">
            <span className="live-status"><i /> Signals updated 4 min ago</span>
            <button className="icon-button alert-button" aria-label="View notifications" onClick={() => toast('You’re all caught up.')}><Bell size={18} /><i /></button>
          </div>
          {mobileMenuOpen && <div className="mobile-menu-popover">{navItems.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} onClick={() => setMobileMenuOpen(false)}><Icon size={17} />{label}</NavLink>)}<NavLink to="/settings" onClick={() => setMobileMenuOpen(false)}><SettingsIcon size={17} />Settings</NavLink></div>}
        </header>
        <div className="page-wrap">
          <AnimatePresence mode="wait">
            <motion.div key={location.pathname} initial={{ opacity: 0, y: 7 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: 0.2 }}>
              <Routes>
                <Route path="/" element={<Dashboard {...props} />} />
                <Route path="/evaluation" element={<Evaluation selectedArea={props.selectedArea} />} />
                <Route path="/rescue" element={<Rescue selectedArea={props.selectedArea} />} />
                <Route path="/places" element={<Places {...props} />} />
                <Route path="/settings" element={<SettingsPage settings={props.settings} setSettings={props.setSettings} />} />
                <Route path="*" element={<Dashboard {...props} />} />
              </Routes>
            </motion.div>
          </AnimatePresence>
        </div>
        <MobileNav />
      </main>
    </div>
  )
}

function MobileNav() {
  return <nav className="mobile-nav" aria-label="Mobile navigation">{navItems.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => isActive ? 'mobile-nav-link active' : 'mobile-nav-link'}><Icon size={19} /><span>{label === 'Rescue hub' ? 'Rescue' : label}</span></NavLink>)}<NavLink to="/settings" className={({ isActive }) => isActive ? 'mobile-nav-link active' : 'mobile-nav-link'}><SettingsIcon size={19} /><span>Settings</span></NavLink></nav>
}

function PageHeading({ eyebrow = 'YOUR LOCAL OUTLOOK', title, subtitle, action }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>{action}</div>
}

function LocationSearch({ selectedArea, setSelectedArea, compact = false }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const filtered = areas.filter((area) => area.name.toLowerCase().includes(query.toLowerCase()))
  const pick = (area) => { setSelectedArea(area); setQuery(''); setOpen(false); toast.success(`${area.name} selected`) }
  return <div className={`location-search ${compact ? 'compact' : ''}`}>
    <Search size={18} aria-hidden="true" />
    <input aria-label="Search an area" value={query} onChange={(event) => { setQuery(event.target.value); setOpen(true) }} onFocus={() => setOpen(true)} onKeyDown={(event) => { if (event.key === 'Enter' && filtered[0]) pick(filtered[0]); if (event.key === 'Escape') setOpen(false) }} placeholder="Search an area..." />
    {query && <button aria-label="Clear search" className="clear-search" onClick={() => setQuery('')}><X size={15} /></button>}
    {!query && <button aria-label="Use current area" className="locate-small" onClick={() => pick(areas[0])}><LocateFixed size={17} /></button>}
    {open && query && <><button className="dismiss-layer" aria-label="Close suggestions" onClick={() => setOpen(false)} /><div className="search-results">{filtered.length ? filtered.map((area) => <button key={area.name} onClick={() => pick(area)}><MapPin size={16} /><span><strong>{area.name}</strong><small>{area.region}</small></span><ArrowRight size={15} /></button>) : <div className="no-results">No areas found. Try Coimbatore or Ooty.</div>}</div></>}
    {!compact && <span className="search-current">Checking <strong>{selectedArea.name}</strong></span>}
  </div>
}

function Dashboard({ selectedArea, setSelectedArea, savedPlaces, setSavedPlaces, settings }) {
  const [scenario, setScenario] = useState(42)
  const [mapLayer, setMapLayer] = useState('Flood')
  const [showPicker, setShowPicker] = useState(false)
  const risk = getAreaRisk(selectedArea, scenario)
  const riskCopy = getRiskCopy(risk)
  const chartData = useMemo(() => timelineData.map((item, index) => ({
    ...item,
    value: index < 2 ? item.value : Math.min(95, item.value + Math.round((scenario - 42) * (index - 1) / 4)),
  })), [scenario])
  const saveCurrent = () => {
    if (savedPlaces.some((place) => place.area === selectedArea.name)) return toast('This area is already saved.')
    setSavedPlaces([...savedPlaces, { id: `${Date.now()}`, name: 'Saved place', area: selectedArea.name, type: 'Custom' }])
    toast.success(`${selectedArea.name} added to My places`)
  }

  const [emergencyMode, setEmergencyMode] = useState(false)
  const [emergencyType, setEmergencyType] = useState(null)
  const [condition, setCondition] = useState(null)
  const [lastLocation, setLastLocation] = useState(null)
  const [locationTimestamp, setLocationTimestamp] = useState(null)
  const [aliveInterval, setAliveInterval] = useState(null)

  // Emergency button press
  const triggerEmergency = async (type) => {
    setEmergencyType(type)
    setEmergencyMode(true)
    
    // Get current area info
    const areaInfo = { ...selectedArea }
    
    // Try to get location
    let location = lastLocation
    if (!location) {
      try {
        const pos = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000, maximumAge: 30000 })
        })
        location = { lng: pos.coords.longitude, lat: pos.coords.latitude }
        setLastLocation(location)
        setLocationTimestamp(new Date().toISOString())
      } catch (e) {
        // Use last known or mock location
        location = { lng: areaInfo.center?.[0], lat: areaInfo.center?.[1] }
      }
    }
    
    // Send to backend
    try {
      await fetch(`${API_BASE}/emergency`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, location, area: areaInfo.name, timestamp: new Date().toISOString() })
      })
    } catch (e) {
      // Store locally for offline sync
      const alerts = JSON.parse(localStorage.getItem('terrasafe.emergency-alerts') || '[]')
      alerts.push({ type, location, area: areaInfo.name, timestamp: new Date().toISOString(), offline: true })
      localStorage.setItem('terrasafe.emergency-alerts', JSON.stringify(alerts))
    }
    
    // Show emergency UI
    if (type === 'trapped') {
      setEmergencyMode(true)
      // Start alive interval
      const interval = setInterval(() => {
        // Send "I'm alive" status
        fetch(`${API_BASE}/emergency/alive`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location, timestamp: new Date().toISOString() }) })
          .catch(() => { /* offline storage handled */ })
      }, 30000)
      setAliveInterval(interval)
    }
  }

  // Stop emergency mode
  const stopEmergency = () => {
    setEmergencyMode(false)
    if (aliveInterval) {
      clearInterval(aliveInterval)
      setAliveInterval(null)
    }
    // Send end emergency signal
    fetch(`${API_BASE}/emergency/end`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) })
      .catch(() => {})
  }

  // Condition check
  const checkCondition = async (cond) => {
    setCondition(cond)
    try {
      await fetch(`${API_BASE}/emergency/condition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ condition: cond, location, timestamp: new Date().toISOString() })
      })
    } catch (e) {
      const alerts = JSON.parse(localStorage.getItem('terrasafe.emergency-alerts') || '[]')
      alerts.push({ type: 'condition', condition, location, timestamp: new Date().toISOString(), offline: true })
      localStorage.setItem('terrasafe.emergency-alerts', JSON.stringify(alerts))
    }
  }

  return <>
    <EmergencyQuickStart
      emergencyMode={emergencyMode}
      setEmergencyMode={setEmergencyMode}
      triggerEmergency={triggerEmergency}
      lastLocation={lastLocation}
    />
    <EmergencyPanel
      emergencyMode={emergencyMode}
      onStop={stopEmergency}
      onCondition={checkCondition}
      lastLocation={lastLocation}
      locationTimestamp={locationTimestamp}
    />
    <PageHeading title={<>Know your area.<br className="desktop-break" /> Stay one step ahead.</>} subtitle="Clear environmental intelligence without the complexity." action={<button className="button button-quiet save-location" onClick={saveCurrent}><Bookmark size={16} /> Save area</button>} />
    <EmergencyQuickStart emergencyMode={emergencyMode} setEmergencyMode={setEmergencyMode} triggerEmergency={triggerEmergency} lastLocation={lastLocation} />
    <div className="dashboard-toolbar"><LocationSearch selectedArea={selectedArea} setSelectedArea={setSelectedArea} /><div className="selected-location"><span className="location-pin"><MapPin size={15} /></span><span><small>SELECTED AREA</small><strong>{selectedArea.name}</strong></span><button aria-label="Change selected area" onClick={() => setShowPicker(!showPicker)}><ChevronDown size={16} /></button>{showPicker && <div className="area-picker">{areas.map((area) => <button key={area.name} onClick={() => { setSelectedArea(area); setShowPicker(false) }}><MapPin size={15} />{area.name}<span>{getAreaRisk(area).label}</span></button>)}</div>}</div></div>

    <section className={`risk-hero risk-${risk.key}`} aria-label="Current area risk">
      <div className="risk-hero-copy"><div className="eyebrow">YOUR AREA <span className="eyebrow-dot" /> UPDATED JUST NOW</div><div className="risk-status-line"><span className="risk-orb" /><span className="risk-word">{risk.label}</span><span className="risk-badge">{risk.label.toUpperCase()} RISK</span></div><h2>{riskCopy.title}</h2><p>{riskCopy.description}</p><div className="hero-actions"><Link to="/evaluation" className="button button-dark">Check area risk <ArrowRight size={16} /></Link><Link to="/rescue" className="button button-outline">Open rescue hub <Shield size={16} /></Link></div></div>
      <div className="risk-hero-aside"><div className="risk-ring" style={{ '--ring-color': risk.color }}><div><strong>{risk.percent}</strong><small>outlook</small></div></div><span className="risk-ring-caption">LOCAL CONDITIONS</span><span className="hero-coordinates-note"><ShieldCheck size={14} /> Reviewed across 4 signals</span></div>
      <div className="hero-decoration" aria-hidden="true"><span /><span /><span /></div>
    </section>

    <section className="section-block"><div className="section-heading"><div><div className="eyebrow">LIVE CONDITIONS</div><h2>What’s shaping your outlook</h2></div><button className="text-button" onClick={() => toast('Signal data refreshed just now.')}><Activity size={15} /> Live signals <i className="live-indicator" /></button></div>
      <div className="signal-grid">{signals.map((signal) => <SignalCard key={signal.name} signal={signal} />)}</div>
    </section>

    <div className="dashboard-grid">
      <section className="panel map-panel"><div className="panel-heading"><div><div className="eyebrow">AREA VIEW</div><h2>Ground picture</h2></div><button className="icon-button subtle" aria-label="Open map controls" onClick={() => toast('Map controls are available on the map.')}><SlidersHorizontal size={17} /></button></div><div className="map-layer-row">{['Flood', 'Landslide', 'Heat', 'Wind'].map((layer) => <button key={layer} className={`layer-chip ${mapLayer === layer ? `layer-active ${layer.toLowerCase()}` : ''}`} onClick={() => setMapLayer(layer)}>{layer === 'Flood' ? <CloudRain size={14} /> : layer === 'Landslide' ? <Mountain size={14} /> : layer === 'Heat' ? <Flame size={14} /> : <Wind size={14} />}{layer}</button>)}</div><TerrainMap area={selectedArea} risk={risk.key} layer={mapLayer} terrain3d={settings.terrain3d} satellite={settings.satellite} onAreaSelect={setSelectedArea} /></section>
      <section className="panel pulse-panel"><div className="pulse-top"><div><div className="eyebrow">A QUICK READ</div><h2>TerraSafe Pulse</h2></div><span className="pulse-icon"><Activity size={18} /></span></div><div className="pulse-message"><span className="pulse-status-dot" /><p>{riskCopy.pulse}</p></div><div className="pulse-signals">{[['Rainfall', 'High', 'amber'], ['Soil', 'Moderate', 'green'], ['Wind', 'Normal', 'green']].map(([name, level, color]) => <div key={name}><span className={`mini-dot ${color}`} /><span>{name}</span><strong>{level}</strong></div>)}</div><Link to="/evaluation" className="panel-link">Understand this outlook <ArrowRight size={15} /></Link></section>
    </div>

    <div className="dashboard-grid lower-grid">
      <section className="panel simulation-panel"><div className="panel-heading"><div><div className="eyebrow">PLAN AHEAD</div><h2>Explore a scenario</h2></div><span className="scenario-icon"><CloudRain size={17} /></span></div><p className="panel-intro">What could more rain mean for {selectedArea.name}?</p><div className="slider-labels"><span>Light rain</span><strong>{scenarioLabel(scenario)}</strong><span>Extreme</span></div><input aria-label="Adjust rainfall scenario" className="scenario-slider" type="range" min="0" max="100" value={scenario} onChange={(event) => setScenario(Number(event.target.value))} style={{ '--slider-progress': `${scenario}%` }} /><div className={`scenario-result result-${risk.key}`}><span className="scenario-risk-dot" /><p><strong>{scenario < 35 ? 'Conditions look manageable.' : scenario < 70 ? 'Low-lying areas may become more vulnerable.' : 'A severe rainfall event could increase local flood risk.'}</strong><small>{scenario < 35 ? 'The outlook stays close to current conditions.' : 'This is a scenario, not a forecast.'}</small></p><ArrowUpRight size={17} /></div><div className="scenario-disclaimer"><CircleHelp size={13} /> Illustrative scenario based on local signals</div></section>
      <section className="panel timeline-panel"><div className="panel-heading"><div><div className="eyebrow">TREND AT A GLANCE</div><h2>Risk timeline</h2></div><span className="trend-tag"><ArrowUpRight size={14} /> Trending up</span></div><div className="timeline-chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData} margin={{ top: 12, right: 6, left: -24, bottom: 0 }}><defs><linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#dc9d45" stopOpacity={0.2} /><stop offset="100%" stopColor="#dc9d45" stopOpacity={0.01} /></linearGradient></defs><CartesianGrid vertical={false} stroke="#edf0eb" strokeDasharray="3 4" /><XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: '#849087', fontSize: 11 }} tickMargin={10} /><Tooltip contentStyle={{ border: '1px solid #e9ede8', borderRadius: 8, fontSize: 12 }} formatter={(value) => [`${value}% outlook`, 'Risk outlook']} /><Area type="monotone" dataKey="value" stroke="#d79a45" strokeWidth={2.5} fill="url(#riskFill)" activeDot={{ r: 4, fill: '#d79a45', stroke: '#fff', strokeWidth: 2 }} /></AreaChart></ResponsiveContainer></div><div className="timeline-legend"><span><i className="legend-low" />Past · Low</span><span><i className="legend-watch" />Now · Watch</span><span><i className="legend-forecast" />Forecast · Rising</span></div></section>
    </div>
    <footer className="page-footer"><span><ShieldCheck size={14} /> Made for clearer decisions, not predictions.</span><span>Mock environmental data · Always follow local authority guidance</span></footer>
  </>
}

function SignalCard({ signal }) {
  const Icon = signal.icon === 'rain' ? CloudRain : signal.icon === 'soil' ? Mountain : signal.icon === 'wind' ? Wind : MapIcon
  return <article className="signal-card"><div className={`signal-icon signal-${signal.tone}`}><Icon size={18} /></div><div className="signal-content"><span>{signal.name}</span><strong>{signal.value}</strong><small className={signal.changeTone}><span>{signal.changeTone === 'change-up' ? '↑' : '→'}</span> {signal.change}</small></div><div className={`sparkline spark-${signal.tone}`} aria-hidden="true">{signal.spark.map((height, index) => <i key={index} style={{ height: `${height}%` }} />)}</div></article>
}

function Evaluation({ selectedArea }) {
  const [step, setStep] = useState(3)
  const [details, setDetails] = useState(false)
  const [actionVisible, setActionVisible] = useState(false)
  const risk = getAreaRisk(selectedArea)
  const steps = ['Collect signals', 'Evaluate risk', 'Explain result', 'Recommend action']
  return <><PageHeading eyebrow="A CLOSER LOOK" title="Evaluation" subtitle={`A clear explanation of conditions around ${selectedArea.name}.`} action={<span className="evaluation-fresh"><i /> Updated just now</span>} />
    <section className="panel evaluation-panel"><div className="evaluation-steps">{steps.map((label, index) => <button className={`evaluation-step ${index < step ? 'done' : ''} ${index === step ? 'current' : ''}`} key={label} onClick={() => setStep(index)} aria-label={`Step ${index + 1}: ${label}`}><span className="step-circle">{index < step ? <Check size={14} /> : index + 1}</span><span>{label}</span></button>)}</div><div className="progress-track"><span style={{ width: `${(step / (steps.length - 1)) * 100}%` }} /></div>
      <div className="evaluation-result"><div className="result-icon"><AlertTriangle size={21} /></div><div><span className="eyebrow">CURRENT ASSESSMENT</span><h2>{selectedArea.name} is under <span className="text-watch">{risk.label}</span></h2><p>Conditions deserve attention, but there’s time to stay informed and prepared.</p></div><span className="risk-badge">{risk.label.toUpperCase()}</span></div>
      <div className="explanation-block"><div className="explanation-title"><Sparkles size={17} /><h3>Why are we showing {risk.label}?</h3></div><p className="explanation-lead">Rainfall is rising while the ground is already holding moderate moisture. Together, these conditions can make low-lying areas more sensitive to further rain.</p><div className="reason-grid">{[['Rainfall', 'High', 'amber', CloudRain, 'Increasing'], ['Soil moisture', 'Moderate', 'green', Mountain, 'Elevated'], ['Terrain', 'Steep', 'amber', MapIcon, 'Local factor'], ['Recent pattern', 'Rising', 'amber', Activity, 'Past 24 hours']].map(([name, value, tone, Icon, note]) => <div className="reason-card" key={name}><span className={`reason-icon ${tone}`}><Icon size={17} /></span><span className="reason-copy"><small>{name}</small><strong>{value}</strong></span><span className={`reason-trend ${tone}`}>{note}</span></div>)}</div><div className="signal-count"><span className="signal-count-dots"><i /><i /><i /><i /></span> 3 signals contributed to this result</div><button className="analysis-toggle" onClick={() => setDetails(!details)}>{details ? 'Hide analysis details' : 'View analysis details'}<ChevronDown className={details ? 'rotate' : ''} size={15} /></button>{details && <div className="analysis-details"><strong>How this assessment works</strong><p>Local rainfall, soil moisture, terrain, and recent patterns are compared with typical conditions. The combined signals inform an area-level outlook; they are not a substitute for official weather alerts.</p><div><span>Data confidence</span><strong>Good · 4 signal groups</strong></div></div>}</div>
      <button className="button button-dark evaluation-cta" onClick={() => setActionVisible(!actionVisible)}>See recommended action <ArrowRight size={16} /></button>{actionVisible && <div className="action-recommendation"><ShieldCheck size={20} /><div><strong>Stay aware of local updates</strong><p>Keep your phone charged, avoid flood-prone routes during heavy rain, and check official local advisories.</p></div></div>}
    </section><div className="data-note"><CircleHelp size={14} /> TerraSafe uses illustrative mock signals in this preview. Assessments are not emergency forecasts.</div>
  </>
}

function Rescue({ selectedArea }) {
  const [guide, setGuide] = useState(false)
  const [layer, setLayer] = useState('Flood')
  const selectedZone = safeZones[0]
  return <><PageHeading eyebrow="HELPFUL, NOT ALARMING" title="Rescue hub" subtitle={`Practical options for ${selectedArea.name}, all in one place.`} action={<button className="button button-danger" onClick={() => toast.error('For immediate danger, contact your local emergency services.')}><AlertTriangle size={16} /> Get help</button>} />
    <div className="rescue-banner"><div className="rescue-banner-icon"><ShieldCheck size={23} /></div><div><span className="eyebrow">CALM MODE</span><h2>You’re not alone. Start with the next safe step.</h2><p>Follow local emergency guidance. These suggested resources are illustrative.</p></div></div>
    <section className="panel rescue-map-panel"><div className="panel-heading"><div><div className="eyebrow">NEAR {selectedArea.name.toUpperCase()}</div><h2>{guide ? 'Suggested route' : 'Nearby safe places'}</h2></div><div className="map-legend"><span><i className="legend-safe" />Safe place</span><span><i className="legend-risk" />Risk area</span></div></div><div className="map-layer-row">{['Flood', 'Landslide', 'Heat', 'Wind'].map((item) => <button key={item} className={`layer-chip ${layer === item ? 'layer-active' : ''}`} onClick={() => setLayer(item)}>{item === 'Flood' ? <CloudRain size={14} /> : item === 'Landslide' ? <Mountain size={14} /> : item === 'Heat' ? <Flame size={14} /> : <Wind size={14} />}{item}</button>)}</div><TerrainMap area={selectedArea} risk="watch" layer={layer} rescue guide={guide} />
      {guide && <div className="route-details"><span className="route-symbol"><Navigation size={17} /></span><div><small>RECOMMENDED SAFE ZONE</small><strong>{selectedZone.name}</strong><span>Follow the highlighted route · about {selectedZone.minutes} min on foot</span></div><button onClick={() => setGuide(false)} aria-label="Close route guidance"><X size={17} /></button></div>}</section>
    <div className="rescue-action-grid"><EmergencyAction icon={MapPin} color="green" title="Find safe zone" text="See designated places nearby." onClick={() => { setGuide(false); toast('Showing nearby safe places on the map.') }} /><EmergencyAction icon={Compass} color="amber" title={guide ? 'Hide directions' : 'Guide me'} text="A simple route to a suggested safe place." onClick={() => setGuide(!guide)} /><EmergencyAction icon={Navigation} color="red" title="Emergency contacts" text="Know who to call when it matters." onClick={() => toast('Local emergency numbers vary by area. Follow official local guidance.')} /></div>
    <div className="rescue-disclaimer"><AlertTriangle size={15} /><p>Safe-zone locations and routes shown here are mock examples. Confirm shelters and routes with local authorities before travelling.</p></div>
  </>
}

function EmergencyAction({ icon: Icon, color, title, text, onClick }) {
  return <button className="emergency-action" onClick={onClick}><span className={`emergency-icon ${color}`}><Icon size={20} /></span><span><strong>{title}</strong><small>{text}</small></span><ArrowRight size={17} /></button>
}

function Places({ selectedArea, savedPlaces, setSavedPlaces, setSelectedArea }) {
  const [adding, setAdding] = useState(false)
  const [newName, setNewName] = useState('')
  const [newArea, setNewArea] = useState(areas[0].name)
  const [editingId, setEditingId] = useState(null)
  const addPlace = (event) => { event.preventDefault(); if (!newName.trim()) return; setSavedPlaces([...savedPlaces, { id: `${Date.now()}`, name: newName.trim(), area: newArea, type: 'Custom' }]); setNewName(''); setAdding(false); toast.success('Place saved') }
  const [editingPlace, setEditingPlace] = useState(null)
  const updatePlace = (event) => { event.preventDefault(); if (!newName.trim() || !editingPlace) return; setSavedPlaces(savedPlaces.map((item) => item.id === editingPlace.id ? { ...item, name: newName.trim() } : item)); setNewName(''); setEditingPlace(null); setEditingId(null); toast.success('Place updated') }
  return <><PageHeading eyebrow="THE PLACES THAT MATTER" title="My places" subtitle="Keep an eye on home, work, and the places you care about." action={<button className="button button-dark" onClick={() => setAdding(true)}><Plus size={16} /> Add a place</button>} />
    <div className="places-current"><span className="location-pin"><MapPin size={15} /></span><div><small>YOU’RE CURRENTLY CHECKING</small><strong>{selectedArea.name}</strong></div><span className="current-pill">ACTIVE</span></div>
    {savedPlaces.length ? <div className="places-grid">{savedPlaces.map((place, index) => { const area = areas.find((item) => item.name === place.area) || areas[0]; const placeRisk = getAreaRisk(area); return <article className="place-card" key={place.id}><div className="place-card-top"><span className={`place-type-icon place-type-${index % 4}`}>{place.type === 'Home' ? <Home size={18} /> : place.type === 'College' ? <Bookmark size={18} /> : place.type === 'Family' ? <Shield size={18} /> : <MapPin size={18} />}</span><button className="icon-button subtle" aria-label={`Options for ${place.name}`} onClick={() => setEditingId(editingId === place.id ? null : place.id)}><Menu size={17} /></button>{editingId === place.id && <div className="place-options"><button onClick={() => { setNewName(place.name); setEditingPlace(place); setEditingId(null) }}>Edit name</button><button className="delete-option" onClick={() => { setSavedPlaces(savedPlaces.filter((item) => item.id !== place.id)); toast('Place removed') }}>Remove place</button></div>}</div><span className="place-type-label">{place.type}</span><h2>{place.name}</h2><p><MapPin size={14} /> {place.area}</p><div className={`place-risk place-risk-${placeRisk.key}`}><span className="risk-orb" /><strong>{placeRisk.label}</strong><small>Current outlook</small></div><button className="place-check" onClick={() => { setSelectedArea(area); toast.success(`Now checking ${area.name}`) }}>Check this area <ArrowRight size={15} /></button></article> })}</div> : <div className="empty-state"><span><MapPin size={22} /></span><h2>No saved places yet.</h2><p>Add Home or College to quickly monitor your important areas.</p><button className="button button-dark" onClick={() => setAdding(true)}><Plus size={16} /> Add a place</button></div>}
    {(adding || editingPlace) && <div className="modal-backdrop" role="presentation" onClick={() => { setAdding(false); setEditingPlace(null) }}><form className="place-modal" onSubmit={editingPlace ? updatePlace : addPlace} onClick={(event) => event.stopPropagation()}><div className="modal-heading"><div><span className="eyebrow">MY PLACES</span><h2>{editingPlace ? 'Edit place' : 'Add a place'}</h2></div><button type="button" className="icon-button subtle" aria-label="Close dialog" onClick={() => { setAdding(false); setEditingPlace(null) }}><X size={18} /></button></div><label>Place name<input autoFocus value={newName} onChange={(event) => setNewName(event.target.value)} placeholder="e.g. Family home" required /></label>{!editingPlace && <label>Area<select value={newArea} onChange={(event) => setNewArea(event.target.value)}>{areas.map((area) => <option key={area.name}>{area.name}</option>)}</select></label>}<div className="modal-actions"><button type="button" className="button button-quiet" onClick={() => { setAdding(false); setEditingPlace(null) }}>Cancel</button><button className="button button-dark" type="submit"><Check size={16} /> {editingPlace ? 'Save changes' : 'Save place'}</button></div></form></div>}
  </>
}

function SettingsPage({ settings, setSettings }) {
  const update = (key, value) => { setSettings({ ...settings, [key]: value }); toast.success('Preference saved') }
  return <><PageHeading eyebrow="MAKE IT YOURS" title="Settings" subtitle="A few thoughtful choices to make TerraSafe work for you." />
    <div className="settings-layout"><div className="settings-main"><SettingsSection title="Notifications" subtitle="Choose which updates reach you."><SettingToggle title="Early warning alerts" description="Get a heads-up when local conditions change." checked={settings.earlyWarnings} onChange={(value) => update('earlyWarnings', value)} /><SettingToggle title="Location-based alerts" description="Only receive alerts for places you follow." checked={settings.locationAlerts} onChange={(value) => update('locationAlerts', value)} /></SettingsSection>
      <SettingsSection title="Map preferences" subtitle="Tune the way your local map looks."><SettingToggle title="Terrain view" description="Bring elevation and landform into view." checked={settings.terrain3d} onChange={(value) => update('terrain3d', value)} /><SettingToggle title="Satellite imagery" description="Use satellite-style tiles when available." checked={settings.satellite} onChange={(value) => update('satellite', value)} /></SettingsSection>
      <SettingsSection title="Preferences" subtitle="How information is shown to you."><SettingSelect title="Units" value={settings.units} options={['Metric', 'Imperial']} onChange={(value) => update('units', value)} /><SettingSelect title="Theme" value={settings.theme} options={['Light', 'System']} onChange={(value) => update('theme', value)} /><SettingSelect title="Language" value={settings.language} options={['English', 'Tamil', 'Hindi']} onChange={(value) => update('language', value)} /></SettingsSection></div>
      <aside className="settings-aside"><div className="source-card"><span className="source-icon"><Layers size={19} /></span><span className="eyebrow">DATA CONNECTIONS</span><strong>13</strong><h3>environmental sources connected</h3><p>Rainfall, terrain, land cover, and more are represented in this preview.</p><div className="source-status"><i /> All systems operational</div></div><div className="settings-version"><ShieldCheck size={16} /><span><strong>TerraSafe preview</strong><small>Mock data · Frontend only</small></span></div></aside></div>
  </>
}

function SettingsSection({ title, subtitle, children }) { return <section className="settings-section"><div className="settings-section-title"><h2>{title}</h2><p>{subtitle}</p></div><div className="settings-controls">{children}</div></section> }
function SettingToggle({ title, description, checked, onChange }) { return <div className="setting-row"><span><strong>{title}</strong><small>{description}</small></span><button className={`toggle ${checked ? 'on' : ''}`} role="switch" aria-checked={checked} aria-label={title} onClick={() => onChange(!checked)}><i /></button></div> }
function SettingSelect({ title, value, options, onChange }) { return <label className="setting-row"><span><strong>{title}</strong><small>Choose your preferred {title.toLowerCase()}.</small></span><select value={value} onChange={(event) => onChange(event.target.value)} aria-label={title}>{options.map((option) => <option key={option}>{option}</option>)}</select></label> }

function scenarioLabel(value) { return value < 25 ? 'Light' : value < 52 ? 'Steady' : value < 78 ? 'Heavy' : 'Extreme' }

export default App
