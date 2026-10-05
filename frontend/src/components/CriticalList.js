/* Critical Priority List Component */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

function CriticalList() {
  const [survivors, setSurvivors] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    axios.get('/api/survivors?priority=CRITICAL')
      .then(response => {
        setSurvivors(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching critical survivors:', err);
        setLoading(false);
      });
  }, []);
  
  if (loading) {
    return <div>Loading critical survivors...</div>;
  }
  
  return (
    <div className="priority-list critical">
      <h3>CRITICAL ({survivors.length})</h3>
      {survivors.length === 0 ? (
        <p>No critical priority survivors.</p>
      ) : (
        <ul>
          {survivors.map(survivor => (
            <li key={survivor._id} className="survivor-item">
              <div className="survivor-info">
                <strong>{survivor.survivorId}</strong>
                <span style={{ color: '#e74c3c', fontSize: '0.8em', marginLeft: '10px' }}>CRITICAL</span>
              </div>
              <div className="survivor-details">
                <span>Status: {survivor.status}</span>
                <span>Priority: {survivor.priority}</span>
                <span>Confidence: {survivor.searchConfidence || 0}%</span>
              </div>
              <div className="survivor-actions">
                <button style={{ marginRight: '5px' }} className="btn-small">Guide</button>
                <button className="btn-small">Location</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default CriticalList;