/* Household List Component */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

function HouseholdList() {
  const [households, setHouseholds] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    axios.get('/api/households')
      .then(response => {
        setHouseholds(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching households:', err);
        setLoading(false);
      });
  }, []);
  
  if (loading) {
    return <div>Loading households...</div>;
  }
  
  return (
    <div className="household-list">
      <h2>Registered Households</h2>
      {households.length === 0 ? (
        <p>No registered households yet.</p>
      ) : (
        <ul>
          {households.map(household => (
            <li key={household._id} className="household-item">
              <div className="household-header">
                <strong>House {household.householdId}</strong>
                <span style={{ float: 'right', fontSize: '0.8em', color: '#666' }}>
                  {household.totalResidents} residents
                </span>
              </div>
              <div className="household-residents">
                {household.residents?.map((resident, i) => (
                  <span key={i} style={{
                    display: 'block', margin: '2px 0',
                    fontSize: '0.85em'
                  }}>
                    {resident.name || 'Unnamed'} - 
                    {resident.ageCategory} 
                    {resident.status ? `— ${resident.status}` : ''}
                  </span>
                ))}
              </div>
              <div className="household-status">
                Safe: {household.residents?.filter(r => r.status === 'SAFE').length || 0}
                {household.residents?.filter(r => r.status === 'RESCUED').length > 0 && ` | Rescued: ${household.residents.filter(r => r.status === 'RESCUED').length || 0}`}
                {household.getUnaccountedCount() > 0 && ` | Unaccounted: ${household.getUnaccountedCount()}`}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default HouseholdList;