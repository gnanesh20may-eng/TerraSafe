/* Rescue Map Component - Displays all rescue-related data on a map */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

function RescueMap() {
  const [mapData, setMapData] = useState({
    survivors: [],
    households: [],
    impactSnapshots: [],
    bluetoothObservations: [],
    rescueFindings: [],
  });
  
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Fetch all map data
    Promise.all([
      axios.get('/api/map'),
      axios.get('/api/survivors'),
      axios.get('/api/households'),
      axios.get('/api/impacts'),
      axios.get('/api/map/bluetooth'),
    ]).then(([mapResp, survivorsResp, householdsResp, impactsResp, bluetoothResp]) => {
      setMapData({
        survivors: survivorsResp.data,
        households: householdsResp.data,
        impactSnapshots: impactsResp.data,
        bluetoothObservations: bluetoothResp.data,
      });
      setLoading(false);
    }).catch(err => {
      console.error('Error fetching map data:', err);
      setLoading(false);
    });
  }, []);
  
  // Color coding for survivor status
  const getStatusColor = (status) => {
    const colors = {
      SAFE: '#27ae60',
      NEEDS_HELP: '#e67e22',
      UNACCOUNTED: '#e74c3c',
      POSSIBLY_TRAPPED: '#9b59b6',
      SIGNAL_DETECTED: '#f1c40f',
      RESCUED: '#2ecc71',
      UNKNOWN: '#95a5a6',
    };
    return colors[status] || '#95a5a6';
  };
  
  // Priority color
  const getPriorityColor = (priority) => {
    const colors = {
      CRITICAL: '#e74c3c',
      HIGH: '#f39c12',
      MEDIUM: '#f1c40f',
      LOW: '#27ae60',
    };
    return colors[priority] || '#95a5a6';
  };
  
  if (loading) {
    return (
      <div className="map-loading">
        <h2>Loading Rescue Map</h2>
        <p>Fetching active incident data...</p>
      </div>
    );
  }
  
  return (
    <div className="rescue-map-container">
      <h2>Rescue Search Map</h2>
      
      <div className="map-legend">
        <div style={{ display: 'flex', gap: 15, marginBottom: 10 }}>
          <div style={{
            width: 12, height: 12, borderRadius: 50,
            background: '#27ae60', marginRight: 5
          }}/> SAFE
          <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ color: '#e74c3c' }}>🟥 UNACCOUNTED</span>
            <span style={{ fontSize: '0.8em' }}>•</span>
            <span style={{ color: '#f39c12' }}>🟧 NEEDS HELP</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ color: '#9b59b6' }}>🟦 POSSIBLY TRAPPED</span>
            <span style={{ fontSize: '0.8em' }}>•</span>
            <span style={{ color: '#f1c40f' }}>🟨 SIGNAL DETECTED</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ color: '#2ecc71' }}>🟩 RESCUED</span>
          </div>
        </div>
      </div>
      
      <div className="map-summary">
        <strong>Unaccounted:</strong> {mapData.survivors.filter(s => s.status === 'UNACCOUNTED').length}
        <strong> | Safe:</strong> {mapData.survivors.filter(s => s.status === 'SAFE').length}
        <strong> | Rescued:</strong> {mapData.survivors.filter(s => s.status === 'RESCUED').length}
      </div>
      
      <div className="map-filters">
        <button className="filter-btn active" data-filter="all">All</button>
        <button className="filter-btn" data-filter="missing">Missing</button>
        <button className="filter-btn" data-filter="signal">Signal Detected</button>
        <button className="filter-btn" data-filter="high">High Priority</button>
        <button className="filter-btn" data-filter="rescued">Rescued</button>
      </div>
      
      <div className="map-observations">
        {/* Impact Snapshots */}
        {mapData.impactSnapshots.map(snapshot => (
          <div key={snapshot.snapshotId} className="map-observation impact" style={{
            background: 'rgba(142, 68, 173, 0.3)',
            padding: '8px 12px',
            margin: '4px 0',
            borderRadius: '4px',
            fontSize: '0.8em'
          }}>
            <strong>IS:</strong> {new Date(snapshot.timestamp).toLocaleTimeString()} 
            at {snapshot.coordinates?.coordinates 
              ? `${snapshot.coordinates.coordinates[1].toFixed(2)}, ${snapshot.coordinates.coordinates[0].toFixed(2)}` 
              : 'N/A'}
          </div>
        ))}
        
        {/* Bluetooth Observations */}
        {mapData.bluetoothObservations.map(obs => (
          <div key={obs._id} className="map-observation bt" style={{
            background: 'rgba(231, 76, 60, 0.3)',
            padding: '8px 12px',
            margin: '4px 0',
            borderRadius: '4px',
            fontSize: '0.8em'
          }}>
            <strong>BT:</strong> RSSI {obs.rssi} dBm ({obs.signalTrend}) 
            at {new Date(obs.recordedAt).toLocaleTimeString()}
          </div>
        ))}
        
        {/* Rescue Findings */}
        {mapData.rescueFindings.map(finding => (
          <div key={finding._id} className="map-observation found" style={{
            background: 'rgba(46, 204, 113, 0.3)',
            padding: '8px 12px',
            margin: '4px 0',
            borderRadius: '4px',
            fontSize: '0.8em'
          }}>
            <strong>FOUND:</strong> {finding.survivor ? finding.survivor.survivorId : 'Unknown'} 
            at {new Date(finding.foundAt).toLocaleTimeString()}
          </div>
        ))}
      </div>
    </div>
  );
}

export default RescueMap;