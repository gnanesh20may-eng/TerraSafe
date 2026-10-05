/* Impact Snapshot List Component */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

function ImpactList() {
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    axios.get('/api/impacts')
      .then(response => {
        setSnapshots(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching impact snapshots:', err);
        setLoading(false);
      });
  }, []);
  
  if (loading) {
    return <div>Loading impact snapshots...</div>;
  }
  
  return (
    <div className="impact-list">
      <h2>Recent Impact Snapshots</h2>
      {snapshots.length === 0 ? (
        <p>No impact snapshots yet.</p>
      ) : (
        <ul>
          {snapshots.slice(0, 20).map(snapshot => (
            <li key={snapshot.snapshotId} className="snapshot-item">
              <div className="snapshot-info">
                <strong>Time:</strong> {new Date(snapshot.timestamp).toLocaleTimeString()}
                <br />
                <strong>Location:</strong> {snapshot.coordinates ? 
                  `(${snapshot.coordinates.coordinates[1].toFixed(4)}, {snapshot.coordinates.coordinates[0].toFixed(4)})` : 'N/A'}
                <br />
                <strong>Battery:</strong> {snapshot.batteryPercentage}%
                <br />
                <strong>GPS Accuracy:</strong> {snapshot.gpsAccuracy || 'N/A'} m
                <br />
                <strong>User Response:</strong> {snapshot.userResponse || 'No response'}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ImpactList;