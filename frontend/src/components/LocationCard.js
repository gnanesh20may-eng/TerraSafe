/* Last Known Location Card Component */

import React, { useState } from 'react';

function LocationCard() {
  // Sample data - in real app this would come from API
  const sampleLocation = {
    personId: 'P-1042',
    lastLocation: '11.xxxx, 78.xxxx',
    lastUpdate: '7:42:15 PM',
    gpsAccuracy: '8 m',
    battery: '60%',
    status: 'UNACCOUNTED'
  };
  
  return (
    <div className="location-card">
      <h2>Last Known Location</h2>
      
      <div className="person-info">
        <strong>Person:</strong> {sampleLocation.personId}
      </div>
      
      <div className="location-details">
        <p><strong>Last location:</strong> {sampleLocation.lastLocation}</p>
        <p><strong>Last update:</strong> {sampleLocation.lastUpdate}</p>
        <p><strong>GPS accuracy:</strong> {sampleLocation.gpsAccuracy}</p>
        <p><strong>Battery:</strong> {sampleLocation.battery}</p>
        <p><strong>Status:</strong> 
          <span style={{
            color: sampleLocation.status === 'UNACCOUNTED' ? '#e74c3c' : 
                   sampleLocation.status === 'SAFE' ? '#27ae60' : '#f39c12'
          }}>
            {sampleLocation.status}
          </span>
        </p>
      </div>
      
      <button style={{ marginTop: '10px', padding: '8px 16px' }}>
        View on Map
      </button>
    </div>
  );
}

export default LocationCard;