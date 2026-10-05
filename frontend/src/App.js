/**
 * Landslide Prediction + Rescue Intelligence - Frontend
 * 
 * This frontend extends the existing prediction application with post-landslide
 * rescue capabilities. It works alongside the existing prediction system rather
 * than replacing it.
 */

import React from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import axios from 'axios';

// Import styles
import './App.css';

// Main App component
function App() {
  const navigate = useNavigate();
  
  // Check auth status on mount
  React.useEffect(() => {
    axios.get('/api/user/me').then(response => {
      const userRole = response.data.role;
      
      // Redirect based on role and available features
      if (userRole === 'rescueWorker' || userRole === 'rescueCoordinator') {
        navigate('/rescue');
      } else {
        navigate('/');
      }
    }).catch(() => {
      // Not authenticated, go to home
      navigate('/');
    });
  }, [navigate]);
  
  return null; // Loading will redirect
}

// Home page - shows prediction integration
function HomePage() {
  return (
    <div className="home-page">
      <h1>Landslide Prediction & Early Warning</h1>
      <p>AI-based landslide risk prediction and monitoring system</p>
      
      <div className="features">
        <div className="feature-card">
          <h3>Prediction</h3>
          <p>Real-time landslide risk assessment</p>
        </div>
        <div className="feature-card">
          <h3>Monitoring</h3>
          <p>Continuous monitoring of risk areas</p>
        </div>
        <div className="feature-card">
          <h3>Rescue Mode</h3>
          <p>Post-landslide survivor detection and rescue intelligence</p>
        </div>
      </div>
      
      <button onClick={() => window.location.href='/api/user/me'}>Check Role</button>
    </div>
  );
}

// Rescue Mode page - main rescue dashboard
function RescuePage() {
  return (
    <div className="rescue-page">
      <h1>Rescue Mode</h1>
      <p>Post-landslide survivor detection and rescue intelligence</p>
      
      <div className="rescue-summary">
        <h2>Active Incident</h2>
        <p>Landslide Event #LS-2026-001</p>
        <div className "summary-stats">
          <div className="stat">
            <span>24</span>
            <affected households />
          </div>
          <div className="stat">
            <span>87</span>
            <EstimatedPeople />
          </div>
          <div className="stat">
            <span>61</span>
            <ConfirmedSafe />
          </div>
        </div>
      </div>
      
      <div className="search-queue">
        <h2>Search Priority</h2>
        <CriticalList />
        <HighList />
        <MediumList />
      </div>
      
      <RescueMap />
    </div>
  );
}

// Impact Snapshot page
function ImpactSnapshotPage() {
  return (
    <div className="impact-snapshot-page">
      <h1>Impact Snapshot</h1>
      <p>Capture and manage impact events from smartphones</p>
      
      <ImpactForm />
      <ImpactList />
    </div>
  );
}

// Survival Mode page
function SurvivalModePage() {
  return (
    <div className="survival-mode-page">
      <h1>🚨 SURVIVAL MODE</h1>
      <p>Stay calm. Save your energy.</p>
      
      <div className="survival-info">
        <p>Cover your nose and mouth from dust.</p>
        <p>Do not move unnecessarily.</p>
        <p>If safe, tap on a solid object: TAP TAP TAP · PAUSE · TAP TAP TAP</p>
      </div>
      
      <div className="battery-status">
        <p>Battery: <span id="battery">60%</span></p>
        <p>Emergency status: <span id="status">ACTIVE</span></p>
      </div>
    </div>
  );
}

// Last Known Location page
function LastKnownLocationPage() {
  return (
    <div className="last-known-location-page">
      <h1>Last Known Location</h1>
      <p>Displaying last known GPS position before communication was lost</p>
      
      <LocationCard />
      <MapMarker />
    </div>
  );
}

// Bluetooth Search page
function BluetoothSearchPage() {
  return (
    <div className="bluetooth-search-page">
      <h1>Bluetooth Proximity Search</h1>
      <p>Device-assisted proximity feature using Bluetooth</p>
      
      <ProximityScanner />
      <SignalHistory />
    </div>
  );
}

// Sound Listening Mode page
function SoundListeningPage() {
  return (
    <div className="sound-listening-page">
      <h1>LISTENING MODE</h1>
      <p>Microphone: ACTIVE</p>
      
      <BeaconStatus />
      <SearchPoints />
    </div>
  );
}

// Households page
function HouseholdsPage() {
  return (
    <div className="households-page">
      <h1>Household Registry</h1>
      <p>Registered households and resident information</p>
      
      <HouseholdList />
      <AddHouseholdForm />
    </div>
  );
}

export default App;