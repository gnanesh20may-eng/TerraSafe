import { useEffect, useState, useCallback } from 'react'
import { AlertTriangle, Bell, Check, Clock, ChevronDown, Loader2, RefreshCw, Shield, X, Zap } from 'lucide-react'
import { alertsApi } from '../services/api.js'
import toast from 'react-hot-toast'

const statusColors = {
  NEW: 'risk-low',
  ACKNOWLEDGED: 'risk-watch',
  ACTIVE: 'risk-high',
  RESOLVED: 'risk-resolved',
}

function AlertsPage({ selectedArea, settings }) {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stale, setStale] = useState(false)
  const [preferences, setPreferences] = useState(null)
  const [prefsLoading, setPrefsLoading] = useState(true)
  const [showPrefs, setShowPrefs] = useState(false)

  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await alertsApi.list(100)
      setAlerts(data.alerts || [])
      setStale(false)
    } catch (err) {
      setError(err.message)
      setStale(true)
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchPreferences = useCallback(async () => {
    try {
      setPrefsLoading(true)
      const data = await alertsApi.getPreferences()
      setPreferences(data.preferences)
    } catch (err) {
      console.warn('Failed to load preferences:', err)
    } finally {
      setPrefsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAlerts()
    fetchPreferences()
    const interval = setInterval(fetchAlerts, 60000)
    return () => clearInterval(interval)
  }, [fetchAlerts, fetchPreferences])

  useEffect(() => {
    if (alerts.length > 0) {
      const latest = new Date(Math.max(...alerts.map(a => new Date(a.updated_at || a.created_at))))
      const staleThreshold = 5 * 60 * 1000
      if (Date.now() - latest.getTime() > staleThreshold) {
        setStale(true)
      }
    }
  }, [alerts])

  const handleTransition = async (alertId, event) => {
    try {
      await alertsApi.transition(alertId, event)
      toast.success(`Alert ${event.toLowerCase()}`)
      fetchAlerts()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const formatTime = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getRiskBadge = (level) => {
    const colors = {
      LOW: 'risk-low',
      WATCH: 'risk-watch',
      HIGH: 'risk-high',
      CRITICAL: 'risk-critical',
    }
    return <span className={`risk-badge ${colors[level] || 'risk-low'}`}>{level}</span>
  }

  if (loading && alerts.length === 0) {
    return (
      <div className="alerts-page loading">
        <div className="loading-spinner"><Loader2 className="spin" size={32} /></div>
        <p>Loading alerts...</p>
      </div>
    )
  }

  return (
    <div className="alerts-page">
      <div className="page-header-row">
        <div>
          <div className="eyebrow">EARLY WARNING SYSTEM</div>
          <h1>Alerts & Notifications</h1>
          <p>Active alerts for {selectedArea.name}</p>
        </div>
        <button
          className="button button-outline"
          onClick={() => { fetchAlerts(); fetchPreferences(); }}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? 'spin' : ''} /> Refresh
        </button>
      </div>

      {stale && (
        <div className="stale-banner">
          <strong>STALE DATA</strong> Data may be stale. Last updated 5+ minutes ago.
          <button className="button button-ghost button-sm" onClick={fetchAlerts}>
            Refresh now
          </button>
        </div>
      )}

      {/* Preferences Section */}
      <section className="panel preferences-panel">
        <div className="panel-heading" onClick={() => setShowPrefs(!showPrefs)} style={{ cursor: 'pointer' }}>
          <div>
            <h2>Alert Preferences</h2>
            <p>Configure notification channels and thresholds</p>
          </div>
          <ChevronDown className={showPrefs ? 'rotate' : ''} size={20} />
        </div>

        {showPrefs && (
          <div className="prefs-content">
            {prefsLoading ? (
              <div className="loading-spinner"><Loader2 className="spin" size={24} /></div>
            ) : preferences ? (
              <div className="prefs-grid">
                <div className="setting-row">
                  <span><strong>Notify on CRITICAL</strong><small>Immediate notification for critical risk</small></span>
                  <span className="badge">Active</span>
                </div>
                <div className="setting-row">
                  <span><strong>Channels</strong><small>Push, Email, SMS</small></span>
                  <span>{preferences.channels?.join(', ')}</span>
                </div>
              </div>
            ) : (
              <p className="error">Failed to load preferences</p>
            )}
          </div>
        )}
      </section>

      {/* Alerts List */}
      <section className="panel alerts-panel">
        <div className="panel-heading">
          <h2>Active Alerts</h2>
          <span className="alert-count">{alerts.filter(a => a.status !== 'RESOLVED').length} active</span>
        </div>

        {error && (
          <div className="error-banner">
            <AlertTriangle size={16} /> {error}
            <button className="button button-ghost button-sm" onClick={fetchAlerts}>Retry</button>
          </div>
        )}

        {alerts.length === 0 ? (
          <div className="empty-state">
            <Bell size={48} className="empty-icon" />
            <h3>No alerts</h3>
            <p>No active alerts for your area. You'll be notified if conditions change.</p>
          </div>
        ) : (
          <div className="alerts-list">
            {alerts.map(alert => (
              <article
                key={alert.id}
                className={`alert-card ${statusColors[alert.status] || 'risk-low'}`}
              >
                <div className="alert-header">
                  <div className="alert-status">
                    <Zap size={18} />
                    <span className={`status-badge ${statusColors[alert.status] || 'risk-low'}`}>
                      {alert.status}
                    </span>
                  </div>
                  <div className="alert-meta">
                    <span className="alert-risk">{getRiskBadge(alert.risk_level)}</span>
                    <span className="alert-time"><Clock size={12} /> {formatTime(alert.updated_at || alert.created_at)}</span>
                  </div>
                </div>

                <div className="alert-body">
                  <h3>{alert.location}</h3>
                  <p className="alert-message">{alert.message}</p>
                  <div className="alert-details">
                    <span><strong>Zone:</strong> {alert.zone_id}</span>
                    {alert.pincode && <span><strong>Pincode:</strong> {alert.pincode}</span>}
                    <span><strong>Risk Score:</strong> {alert.risk_score}/100</span>
                  </div>
                </div>

                <div className="alert-actions">
                  {alert.status === 'NEW' && (
                    <button 
                      className="button button-primary button-sm"
                      onClick={() => handleTransition(alert.id, 'ACKNOWLEDGED')}
                    >
                      Acknowledge
                    </button>
                  )}
                  {alert.status === 'ACKNOWLEDGED' && (
                    <button
                      className="button button-primary button-sm"
                      onClick={() => handleTransition(alert.id, 'ACTIVE')}
                    >
                      Activate
                    </button>
                  )}
                  {alert.status === 'ACTIVE' && (
                    <button
                      className="button button-primary button-sm"
                      onClick={() => handleTransition(alert.id, 'RESOLVED')}
                    >
                      Resolve
                    </button>
                  )}
                  <button
                    className="button button-ghost button-sm"
                    onClick={() => toast(`Alert ID: ${alert.id}`)}
                  >
                    Details
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default AlertsPage
