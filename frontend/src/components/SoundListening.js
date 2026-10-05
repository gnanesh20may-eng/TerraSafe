/* Sound Listening Mode Component */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SoundListeningMode() {
  const [isListening, setListening] = useState(false);
  const [beaconDetected, setBeaconDetected] = useState(false);
  const [signalLevel, setSignalLevel] = useState(0);
  const [trend, setTrend] = useState('Unknown');
  const [decibelLevel, setDecibelLevel] = useState(0);
  const [searchPoints, setSearchPoints] = useState([
    { id: 1, intensity: 0 },
    { id: 2, intensity: 0 },
    { id: 3, intensity: 0 },
    { id: 4, intensity: 0 },
  ]);
  
  const [windowActive, setWindowActive] = useState(true);
  
  const startListening = async () => {
    setListening(true);
    setBeaconDetected(false);
    
    // Simulate periodic beacon detection
    const interval = setInterval(() => {
      if (!isListening) return;
      
      // Simulate sound level fluctuation
      const newLevel = Math.max(0, Math.min(100, decibelLevel + (Math.random() - 0.5) * 20));
      setDecibelLevel(newLevel);
      
      // Random beacon detection
      const detected = Math.random() > 0.7; // 30% chance
      setBeaconDetected(detected);
      
      if (detected) {
        // Update signal level when beacon detected
        setSignalLevel(Math.min(100, signalLevel + 15));
      }
      
      // Update trend
      const lastPoint = searchPoints[searchPoints.length - 1];
      if (lastPoint) {
        const newIntensity = Math.min(100, lastPoint.intensity + (Math.random() - 0.5) * 25);
        setSearchPoints(prev =>
          prev.map((p, i) =>
            i === searchPoints.length - 1 ? { ...p, intensity: newIntensity } : p
          )
        );
      }
      
      // Determine trend
      if (searchPoints.length >= 2) {
        const prevIntensity = searchPoints[searchPoints.length - 2].intensity;
        if (newLevel > prevIntensity) {
          setTrend('Getting Louder');
        } else if (newLevel < prevIntensity) {
          setTrend('Getting Quieter');
        } else {
          setTrend('Stable');
        }
      }
    }, 1500); // Check every 1.5 seconds
    
    // Auto-stop after 2 minutes for safety
    setTimeout(() => {
      setListening(false);
      clearInterval(interval);
    }, 120000);
  };
  
  const stopListening = () => {
    setListening(false);
  };
  
  const addSearchPoint = (intensity) => {
    setSearchPoints(prev => {
      const newPoints = [...prev, { id: prev.length + 1, intensity }];
      if (newPoints.length > 4) newPoints.shift();
      return newPoints;
    });
  };
  
  const maintainQuietWindow = () => {
    setWindowActive(!windowActive);
    alert('Rescue team should maintain silence for 20-30 seconds while listening. This is an experimental search aid.');
  };
  
  return (
    <div className="sound-listening">
      <h2>LISTENING MODE</h2>
      
      <div className="listening-controls">
        <button onClick={startListening} disabled={isListening} className="btn-primary">
          {isListening ? 'Listening...' : 'Start Listening'}
        </button>
        <button onClick={maintainQuietWindow} className="btn-secondary">
          Quiet Search Window
        </button>
      </div>
      
      {isListening && (
        <div className="listening-status">
          <strong>Microphone:</strong> ACTIVE
          <br />
          <strong>Beacon detected:</strong> {beaconDetected ? 'YES' : 'NO'}
          <br />
          <strong>Signal level:</strong> 
          <div style={{
            width: '100%',
            height: 20,
            background: '#eee',
            borderRadius: 4,
            overflow: 'hidden'
          }}>
            <div style={{
              width: signalLevel + '%',
              height: '100%',
              background: beaconDetected ? '#e74c3c' : '#3498db',
              transition: 'width 0.5s'
            }}></div>
          </div>
          <span>{Math.round(signalLevel)}%</span>
          <br />
          <strong>Trend:</strong> <span 
            style={{ 
              color: trend === 'Getting Louder' ? 'var(--success-color)' : 
                     trend === 'Getting Quieter' ? 'var(--accent-color)' : 
                     '#666'
            }}>
              {trend}
            </span>
        </div>
      )}
      
      <div className="search-points">
        <strong>Search Points:</strong>
        <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
          {searchPoints.map(point => (
            <div key={point.id} style={{
              width: 30,
              height: 30,
              background: point.intensity > 50 ? '#e74c3c' : point.intensity > 25 ? '#f39c12' : '#3498db',
              borderRadius: 5,
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.7em',
              minWidth: 30
            }}>
              {point.intensity}%
            </div>
          ))}
        </div>
      </div>
      
      <p className="important-note">
        <em>
          Important: Do not automatically claim that loudness equals exact distance. 
          Rubber geometry, reflections and noise can distort sound. This is experimental assistance.
        </em>
      </p>
      
      <p className="quiet-warning">
        <em>Press "Quiet Search Window" to maintain silence during listening.</em>
      </p>
    </div>
  );
}

export default SoundListeningMode;