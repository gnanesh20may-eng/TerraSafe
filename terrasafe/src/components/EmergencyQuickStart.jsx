import { useState, useEffect, useRef } from 'react'
import { X, Check, Phone, MapPin, Heart, Users, AlertTriangle, Moon, Battery, Sun, Volume2, Moon as MoonIcon, Mic, Shield, Map, MapPin as MapPinIcon, Menu, Loader2, Pause, Play, AlertCircle, Eye, EyeOff, Mail, MessageCircle, PhoneCall, Info } from 'lucide-react'

function EmergencyQuickStart({ emergencyMode, setEmergencyMode, triggerEmergency, lastLocation }) {
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

  useEffect(() => {
    // Detect if we're in a landslide-prone area or emergency situation
    const checkLandslideRisk = () => {
      // In a real implementation, this would check terrain data
      // For now, just monitor battery and network
    }
    checkLandslideRisk()
  }, [lastLocation])

  const handleTrapped = () => {
    triggerEmergency('trapped')
    setEmergencyMode(true)
  }

  const handleLocation = () => {
    // Get current location
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const location = { lng: pos.coords.longitude, lat: pos.coords.latitude }
        triggerEmergency('location')
        setEmergencyMode(true)
      },
      (err) => {
        // Use last known area center if GPS fails
        triggerEmergency('location')
        setEmergencyMode(true)
      },
      { timeout: 5000, maximumAge: 30000 }
    )
  }

  const handleAlive = () => {
    triggerEmergency('alive')
    setEmergencyMode(true)
  }

  const handleCondition = () => {
    // Show condition check - will be handled by EmergencyPanel
    triggerEmergency('condition')
    setEmergencyMode(true)
  }

  const handleFamily = () => {
    triggerEmergency('family')
    setEmergencyMode(true)
  }

  if (!emergencyMode) {
    return (
      <div
        className="emergency-quick-start-container"
        onClick={() => setEmergencyMode(!emergencyMode)}
        aria-label="Emergency quick start"
        tabindex={0}
      >
        <div className="emergency-quick-start-card">
          <div className="emergency-quick-start-header">
            <span className="emergency-quick-start-title">TERRAFAST EMERGENCY</span>
            <small>Victim to Rescue Communication</small>
          </div>
          <div className="emergency-quick-start-status">
            {lastLocation && (
              <div>
                <MoonIcon size={12} /> Last known: {lastLocation.lat.toFixed(2)}, {lastLocation.lng.toFixed(2)}
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
            {networkStatus === 'online' && <div><Volume2 size={12} /> Online</div>}
            {networkStatus === 'offline' && <div><MoonIcon size={12} /> Offline</div>}
          </div>
          <div className="emergency-quick-start-buttons">
            <button className="emergency-quick-start-btn trapped" onClick={handleTrapped} aria-label="I'm Trapped - Send emergency rescue alert">
              <Phone size={24} /> I'm Trapped
            </button>
            <button className="emergency-quick-start-btn location" onClick={handleLocation} aria-label="Share My Location">
              <MapPin size={24} /> Share My Location
            </button>
            <button className="emergency-quick-start-btn alive" onClick={handleAlive} aria-label="I'm Alive - Send periodic status">
              <Heart size={24} /> I'm Alive
            </button>
            <button className="emergency-quick-start-btn condition" onClick={handleCondition} aria-label="My Condition">
              <AidKit size={24} /> My Condition
            </button>
            <button className="emergency-quick-start-btn family" onClick={handleFamily} aria-label="Alert Family">
              <Users size={24} /> Alert Family
            </button>
          </div>
          <div className="emergency-quick-start-footer">
            <small>Landslide victim communication system • Minimum interaction • Fastest rescue</small>
          </div>
        </div>
      </div>
    )
  }

  // When in emergency mode, show the full EmergencyPanel
  return null
}

export default EmergencyQuickStart