/* Impact Snapshot Form Component */

import React, { useState } from 'react';
import axios from 'axios';

function ImpactForm() {
  const [formData, setFormData] = useState({
    deviceId: '',
    survivorId: '',
    batteryPercentage: 100,
    gpsAccuracy: '',
    accelerometer: { x: 0, y: 0, z: 0, magnitude: 0, eventType: 'Impact' },
    gyroscope: { x: 0, y: 0, z: 0, available: false },
    activityState: 'Unknown',
  });
  
  const [showForm, setShowForm] = useState(true);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/impacts', {
        ...formData,
        timestamp: new Date(),
        location: {
          type: 'Point',
          coordinates: [formData.longitude, formData.latitude],
        },
      });
      alert('Impact snapshot created successfully');
      setShowForm(false);
      setTimeout(() => setShowForm(true), 100);
    } catch (err) {
      alert('Error creating impact snapshot: ' + err.message);
    }
  };
  
  return (
    <div className="impact-form">
      <h2>Capture Impact Snapshot</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Device ID</label>
          <input 
            type="text" 
            name="deviceId" 
            value={formData.deviceId} 
            onChange={handleChange} 
            placeholder="Anonymous device ID" 
            required 
          />
        </div>
        
        <div className="form-group">
          <label>Survivor ID</label>
          <input 
            type="text" 
            name="survivorId" 
            value={formData.survivorId} 
            onChange={handleChange} 
            placeholder="P-1042" 
          />
        </div>
        
        <div className="form-group">
          <label>Battery Percentage</label>
          <input 
            type="number" 
            name="batteryPercentage" 
            value={formData.batteryPercentage} 
            onChange={handleChange} 
            min="0" 
            max="100" 
            required 
          />
        </div>
        
        <div className="form-group">
          <label>GPS Accuracy (meters)</label>
          <input 
            type="number" 
            name="gpsAccuracy" 
            value={formData.gpsAccuracy} 
            onChange={handleChange} 
            placeholder="e.g. 8" 
          />
        </div>
        
        <div className="form-group">
          <label>Accelerometer X</label>
          <input 
            type="number" 
            name="accX" 
            value={formData.accelerometer.x} 
            onChange={handleChange} 
            placeholder="X component" 
          />
        </div>
        
        <div className="form-group">
          <label>Accelerometer Y</label>
          <input 
            type="number" 
            name="accY" 
            value={formData.accelerometer.y} 
            onChange={handleChange} 
            placeholder="Y component" 
          />
        </div>
        
        <div className="form-group">
          <label>Accelerometer Z</label>
          <input 
            type="number" 
            name="accZ" 
            value={formData.accelerometer.z} 
            onChange={handleChange} 
            placeholder="Z component" 
          />
        </div>
        
        <div className="form-group">
          <label>Accelerometer Magnitude</label>
          <input 
            type="number" 
            name="accMagnitude" 
            value={formData.accelerometer.magnitude} 
            onChange={handleChange} 
            placeholder="Magnitude" 
          />
        </div>
        
        <div className="form-group">
          <label>Activity State</label>
          <select 
            name="activityState" 
            value={formData.activityState} 
            onChange={handleChange}
          >
            <option value="Still">Still</option>
            <option value="Walking">Walking</option>
            <option value="Running">Running</option>
            <option value="Vehicle">Vehicle</option>
            <option value="Falling">Falling</option>
            <option value="Unknown">Unknown</option>
          </select>
        </div>
        
        <button type="submit" className="btn-primary">
          Capture Impact Snapshot
        </button>
      </form>
    </div>
  );
}

export default ImpactForm;