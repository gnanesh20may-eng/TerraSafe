import { useState, useEffect, useRef } from 'react'
// API URL from Vercel env var (VITE_API_URL=/api/v1 in production)
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
import { X, Check, Phone, MapPin, AlertTriangle, Battery, Sun, Moon, Volume2, Mic, Shield, Map, MapPin as MapPinIcon, Menu, Loader2, Pause, Play, AlertCircle, AidKit, Users, Heart, Pulse, Zap, Info, ExclamationCircle, Location, Mail, PhoneForward, MessageCircle, PhoneCall, PhoneForwardIncoming, Eye, EyeOff } from 'lucide-react'

function EmergencyPanel({ emergencyMode, onStop, onCondition, lastLocation, locationTimestamp }) {
  const [showPanel, setShowPanel] = useState(false)
  const [networkStatus, setNetworkStatus] = useState('online')
  const [batteryLevel, setBatteryLevel] = useState(navigator?.battery ? navigator.battery.level * 100 : 100)
  const emergencyRef = useRef(null)

  useEffect(() => {
    // Check network status
    const checkNetwork = () => {
      setNetworkStatus(navigator.onLine ? 'online' : 'offline')
    }
    window.addEventListener('online', checkNetwork)
    window.addEventListener('offline', checkNetwork)
    checkNetwork()
    return () => {
      window.removeEventListener('online', checkNetwork)
      window.removeEventListener('offline', checkNetwork)
    }
  }, [])

  useEffect(() => {
    // Update battery level
    if (navigator?.battery) {
      const updateBattery = () => {
        setBatteryLevel(Math.max(0, Math.min(100, navigator.battery.level * 100)))
      }
      updateBattery()
      navigator.battery.onlevelchange = updateBattery
      navigator.battery.onchargingchange = () => {
        // Show charging indicator when in trapped mode
        if (emergencyRef.current?.classList.contains('trapped-mode')) {
          setBatteryLevel(Math.min(100, batteryLevel + 5))
        }
      }
      return () => {
        navigator.battery.onlevelchange = null
        navigator.battery.onchargingchange = null
      }
    }
    return () => {
      if (navigator?.battery) {
        navigator.battery.onlevelchange = null
        navigator.battery.onchargingchange = null
      }
    }
  }, [emergencyMode])

  const triggerEmergency = async (type) => {
    setShowPanel(false)
    onStop()
    onCondition(null)
    
    // In a full implementation, this would send to backend
    // For now, store in localStorage for offline capability
    const alerts = JSON.parse(localStorage.getItem('terrasafe.emergency-alerts') || '[]')
    alerts.push({
      id: Date.now(),
      type,
      timestamp: new Date().toISOString(),
      location: lastLocation,
      locationTimestamp,
      network: networkStatus,
      battery: batteryLevel,
    })
    localStorage.setItem('terrasafe.emergency-alerts', JSON.stringify(alerts))
    
    // Try to send to backend if online
    if (networkStatus === 'online') {
      // Would fetch(`${API_BASE}/emergency`, { method: 'POST', body: ... })
    }
  }

  const sendAliveStatus = () => {
    const alerts = JSON.parse(localStorage.getItem('terrasafe.emergency-alerts') || '[]')
    alerts.push({
      id: Date.now(),
      type: 'alive',
      timestamp: new Date().toISOString(),
      location: lastLocation,
      locationTimestamp,
      network: networkStatus,
      battery: batteryLevel,
    })
    localStorage.setItem('terrasafe.emergency-alerts', JSON.stringify(alerts))
  }

  const checkCondition = (cond) => {
    onCondition(cond)
    const alerts = JSON.parse(localStorage.getItem('terrasafe.emergency-alerts') || '[]')
    alerts.push({
      id: Date.now(),
      type: 'condition',
      condition: cond,
      timestamp: new Date().toISOString(),
      location: lastLocation,
      locationTimestamp,
      network: networkStatus,
      battery: batteryLevel,
    })
    localStorage.setItem('terrasafe.emergency-alerts', JSON.stringify(alerts))
  }

  if (!emergencyMode) {
    return (
      <div
        className="emergency-quick-access"
        onClick={() => setShowPanel(!showPanel)}
        aria-label="Emergency quick access"
        tabindex={0}
      >
        <div className="emergency-quick-access-icon"><AlertTriangle size={24} /></div>
        <div>
          <span className="emergency-quick-access-text">EMERGENCY</span>
          <small>Tap for help</small>
        </div>
      </div>
    )
  }

  return (
    <div className="emergency-panel" ref={emergencyRef}>
      <div className="emergency-panel-header">
        <span className="emergency-panel-title">EMERGENCY MODE</span>
        <button className="emergency-panel-close" onClick={onStop} aria-label="Exit emergency mode"><X size={20} /></button>
      </div>

      <div className="emergency-panel-body">
        {/* Location info */}
        {lastLocation && (
          <div className="emergency-location-info">
            <div><MapPinIcon size={16} /> <strong>Location:</strong> {lastLocation.lat.toFixed(4)}, {lastLocation.lng.toFixed(4)}</div>
            {locationTimestamp && <div><Sun size={12} /> Last updated: {new Date(locationTimestamp).toLocaleTimeString()}</div>}
            {networkStatus === 'online' && <div><Volume2 size={12} /> Network: Online</div>}
            {networkStatus === 'offline' && (
              <div>
                <Moon size={12} /> Network: Offline
                <small>Alerts stored locally, will sync when online</small>
              </div>
            )}
            {batteryLevel !== undefined && (
              <div>
                {batteryLevel < 20 && <Battery size={12} className="critical-battery" />}
                {batteryLevel >= 20 && batteryLevel < 50 && <Battery size={12} className="low-battery" />}
                {batteryLevel >= 50 && <Battery size={12} className="good-battery" />}
                <small>Battery: {Math.round(batteryLevel)}%</small>
              </div>
            )}
          </div>
        )}

        {/* Emergency type selection */}
        <div className="emergency-type-selector">
          <p><strong>What's your emergency?</strong></p>
          <div className="emergency-type-grid">
            <button
              className={`emergency-type-btn ${emergencyType === 'trapped' ? 'active' : ''}`}
              onClick={() => triggerEmergency('trapped')}
              aria-label="I'm trapped - send emergency rescue alert"
            >
              <span><Phone size={20} /> I'm Trapped</span>
            </button>
            <button
              className={`emergency-type-btn ${emergencyType === 'alive' ? 'active' : ''}`}
              onClick={() => triggerEmergency('alive')}
              aria-label="I'm Alive - send periodic status updates"
            >
              <span><Heart size={20} /> I'm Alive</span>
            </button>
            <button
              className={`emergency-type-btn ${emergencyType === 'condition' ? 'active' : ''}`}
              onClick={() => setShowCondition(true)}
              aria-label="Check my condition"
            >
              <span><AidKit size={20} /> My Condition</span>
            </button>
            <button
              className={`emergency-type-btn ${emergencyType === 'family' ? 'active' : ''}`}
              onClick={() => triggerEmergency('family')}
              aria-label="Alert my family"
            >
              <span><Users size={20} /> Alert Family</span>
            </button>
          </div>
        </div>

        {/* Condition check popup */}
        {showCondition && (
          <div className="condition-check-popup">
            <div className="condition-check-header">
              <strong>What's your condition?</strong>
              <button className="condition-check-close" onClick={() => setShowCondition(false)} aria-label="Close"><X size={18} /></button>
            </div>
            <div className="condition-check-options">
              <button className="condition-option" onClick={() => checkCondition('okay') && setShowCondition(false)}>
                <span><Check size={16} /> I am okay</span>
              </button>
              <button className="condition-option" onClick={() => checkCondition('injured') && setShowCondition(false)}>
                <span><AlertTriangle size={16} /> I am injured</span>
              </button>
              <button className="condition-option" onClick={() => checkCondition('cannot_move') && setShowCondition(false)}>
                <span><Moon size={16} /> I cannot move</span>
              </button>
              <button className="condition-option" onClick={() => checkCondition('with_others') && setShowCondition(false)}>
                <span><Users size={16} /> Others are with me</span>
              </button>
            </div>
          </div>
        )}

        {/* Trapped mode controls */}
        {emergencyType === 'trapped' && (
          <div className="trapped-mode-controls">
            <p><strong>Trapped Mode Active</strong></p>
            <div className="trapped-mode-settings">
              <div className="setting-row">
                <span>Battery Saver</span>
                <button className={`toggle ${batteryLevel < 20 ? 'on' : ''}`} aria-label="Toggle battery saver">On</button>
              </div>
              <div className="setting-row">
                <span>Screen Brightness</span>
                <button className={`toggle ${true}`} aria-label="Reduce screen brightness">Dim</button>
              </div>
              <div className="setting-row">
                <span>Transmission Interval</span>
                <select aria-label="Set transmission interval">
                  <option value="30s">30 seconds</option>
                  <option value="60s">60 seconds</option>
                  <option value="5min">5 minutes</option>
                  <option value="10min">10 minutes</option>
                </select>
              </div>
            </div>
            <div className="emergency-instructions">
              <strong>Instructions:</strong>
              <p>1. Stay calm and stay where you are if safe</p>
              <p>2. Rescue teams are en route</p>
              <p>3. Periodic location updates being sent</p>
              <p>4. Say "I'm alive" when you hear rescuers</p>
            </div>
          </div>
        )}

        {/* Family alert */}
        {emergencyType === 'family' && (
          <div className="family-alert">
            <p><strong>Family Alert Message:</strong></p>
            <textarea readonly className="family-alert-text">
SOS: I am affected by a landslide. My last known location is being shared with rescue services. Please be notified.
            </textarea>
            <button onClick={() => {
              // Would send SMS/alert to predefined contacts
              const alerts = JSON.parse(localStorage.getItem('terrasafe.emergency-alerts') || '[]')
              alerts.push({
                id: Date.now(),
                type: 'family_alert',
                message: 'SOS: I am affected by a landslide. My last known location is being shared with rescue services.',
                timestamp: new Date().toISOString(),
                location: lastLocation,
              })
              localStorage.setItem('terrasafe.emergency-alerts', JSON.stringify(alerts))
              setShowPanel(false)
              onStop()
            }}>
              Send Alert
            </button>
          </div>
        )}

        {/* Rescue communication */}
        {emergencyType !== 'trapped' && emergencyType !== 'family' && emergencyType !== null && (
          <div className="rescue-comm">
            <p><strong>Quick Communication:</strong></p>
            <div className="rescue-comm-options">
              <button className="comm-option" onclick="alert('Feature: Send "I can hear you" to rescue team')">I can hear you</button>
              <button className="comm-option" onclick="alert('Feature: Send "I need medical help" to rescue team')">I need medical help</button>
              <button className="comm-option" onclick="alert('Feature: Send "There are 3 people" to rescue team')">There are 3 people</button>
              <button className="comm-option" onclick="alert('Feature: Send "I am inside a building" to rescue team')">I am inside a building</button>
              <button className="comm-option" onclick="alert('Feature: Send "I hear rescuers" to rescue team')">I hear rescuers</button>
            </div>
          </div>
        )}

        {/* Status indicators */}
        <div className="emergency-status-bar">
          <div className="status-item"><Heart size={12} /> Alive: {aliveInterval ? 'Active' : 'Inactive'}</div>
          <div className="status-item"><Location size={12} /> Location: {lastLocation ? 'Updated' : 'Not set'}</div>
          <div className="status-item"><Battery size={12} /> Battery: {batteryLevel !== undefined ? Math.round(batteryLevel) + '%' : 'N/A'}</div>
        </div>
      </div>
    </div>
  )
}

export default EmergencyPanel