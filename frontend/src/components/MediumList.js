/* Medium Priority List Component */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

function MediumList() {
  const [survivors, setSurvivors] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    axios.get('/api/survivors?priority=MEDIUM')
      .then(response => {
        setSurvivors(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching medium priority survivors:', err);
        setLoading(false);
      });
  }, []);
  
  if (loading) {
    return <div>Loading medium priority survivors...</div>;
  }
  
  return (
    <div className="priority-list medium">
      <h3>MEDIUM ({survivors.length})</h3>
      {survivors.length === 0 ? (
        <p>No medium priority survivors.</p>
      ) : (
        <ul>
          {survivors.map(survivor => (
            <li key={survivor._id} className="survivor-item">
              <div className="survivor-info">
                <strong>{survivor.survivorId}</strong>
                <span style={{ color: '#f1c40f', fontSize: '0.8em', marginLeft: '10px' }}>MEDIUM</span>
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

export default MediumList;