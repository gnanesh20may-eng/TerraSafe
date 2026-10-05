/* Bluetooth Proximity Scanner Component */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ProximityScanner() {
  const [rssi, setRssi] = useState(0);
  const [trend, setTrend] = useState('Unknown');
  const [deviceId, setDeviceId] = useState('Unknown device');
  const [scanning, setScanning] = useState(false);
  const [signalHistory, setSignalHistory] = useState([]);
  
  const MAX_HISTORY = 10;
  
  const startScan = async () => {
    setScanning(true);
    try {
      // In a real implementation, this would use native Bluetooth APIs
      // For the prototype, we simulate a scan
      const simulatedRssi = -70 + Math.random() * 30; // Random RSSI between -70 and -40
      setRssi(Math.round(simulatedRssi));
      
      // Add to history
      setSignalHistory(prev => {
        const newEntry = { rssi: simulatedRssi, timestamp: new Date() };
        if (prev.length >= MAX_HISTORY) prev.shift();
        prev.push(newEntry);
        return prev;
      });
      
      // Determine trend based on previous RSSI
      if (signalHistory.length > 0) {
        const prevRssi = signalHistory[signalHistory.length - 1].rssi;
        if (simulatedRssi > prevRssi) {
          setTrend('Getting Stronger');
        } else if (simulatedRssi < prevRssi) {
          setTrend('Getting Weaker');
        } else {
          setTrend('Stable');
        }
      } else {
        setTrend('Unknown');
      }
    } catch (err) {
      console.error('Error during Bluetooth scan:', err);
    } finally {
      setScanning(false);
    }
  };
  
  const determineTrend = (previousRssi) => {
    if (rssi > previousRssi) {
      setTrend('Getting Stronger');
    } else if (rssi < previousRssi) {
      setTrend('Getting Weaker');
    } else {
      setTrend('Stable');
    }
  };
  
  return (
    <div className="bluetooth-scanner">
      <h2>Bluetooth Proximity Search</h2>
      
      <div className="scanner-controls">
        <button onClick={startScan} disabled={scanning} className="btn-primary">
          {scanning ? 'Scanning...' : 'Scan for Devices'}
        </button>
        <span>{scanning ? 'Scanning...' : 'Search for survivor devices'}</span>
      </div>
      
      <div className="signal-reading">
        <strong>RSSI:</strong> {rssi} dBm
        <br />
        <strong>Trend:</strong> <span 
          style={{ 
            color: rssi > -50 ? 'var(--success-color)' : rssi > -80 ? 'var(--warning-color)' : 'var(--accent-color)',
            fontWeight: 'bold' 
          }}>
            {trend}
          </span>
      </div>
      
      {deviceId && (
        <div>
          <strong>Target Device:</strong> {deviceId}
        </div>
      )}
      
      <div className="signal-history">
        <strong>Signal History:</strong>
        <ul>
          {signalHistory.map((entry, i) => (
            <li key={i} style={{ 
              color: entry.rssi > -50 ? 'var(--success-color)' : entry.rssi > -80 ? 'var(--warning-color)' : 'var(--accent-color)',
              fontSize: '0.8em'
            }}>
              Point {i + 1}: RSSI {entry.rssi} dBm
            </li>
          ))}
        </ul>
      </div>
      
      <p className="important-note">
        <em>Important: RSSI is affected by walls, soil, metal, water, orientation 
        and rubble. This is a proximity estimate, not an exact location.</em>
      </p>
    </div>
  );
}

export default ProximityScanner;