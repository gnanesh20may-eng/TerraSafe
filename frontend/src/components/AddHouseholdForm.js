/* Add Household Form Component */

import React, { useState } from 'react';
import axios from 'axios';

function AddHouseholdForm() {
  const [formData, setFormData] = useState({
    householdId: '',
    buildingId: '',
    latitude: '',
    longitude: '',
    totalResidents: 1,
    specialAssistance: 'None',
    petCount: 0,
    emergencyContactName: '',
    emergencyContactPhone: '',
    consentDataSharing: false,
    consentLocationSharing: false,
    consentEmergencyAlerts: false,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const household = new Household({
        householdId: formData.householdId,
        buildingId: formData.buildingId,
        location: {
          type: 'Point',
          coordinates: [parseFloat(formData.longitude), parseFloat(formData.latitude)],
        },
        totalResidents: parseInt(formData.totalResidents),
        residents: [],
        specialAssistance: formData.specialAssistance,
        petCount: parseInt(formData.petCount),
        emergencyContact: {
          name: formData.emergencyContactName,
          phone: formData.emergencyContactPhone,
        },
        consent: {
          dataSharing: formData.consentDataSharing,
          locationSharing: formData.consentLocationSharing,
          emergencyAlerts: formData.consentEmergencyAlerts,
        },
      });

      const response = await axios.post('/api/households', household);
      alert('Household registered successfully');
      setFormData({
        householdId: '',
        buildingId: '',
        latitude: '',
        longitude: '',
        totalResidents: 1,
        specialAssistance: 'None',
        petCount: 0,
        emergencyContactName: '',
        emergencyContactPhone: '',
        consentDataSharing: false,
        consentLocationSharing: false,
        consentEmergencyAlerts: false,
      });
    } catch (err) {
      alert('Error registering household: ' + err.message);
    }
  };

  return (
    <div className="add-household-form">
      <h2>Register New Household</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Household ID</label>
            <input
              type="text"
              name="householdId"
              value={formData.householdId}
              onChange={handleChange}
              placeholder="H-14"
              required
            />
          </div>
          <div className="form-group">
            <label>Building ID</label>
            <input
              type="text"
              name="buildingId"
              value={formData.buildingId}
              onChange={handleChange}
              placeholder="B-14"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>GPS Location</label>
            <div style={{ display: 'flex', gap: 10 }}>
              <input
                type="number"
                name="latitude"
                value={formData.latitude}
                onChange={handleChange}
                placeholder="Lat"
                step="0.0001"
                required
              />
              <input
                type="number"
                name="longitude"
                value={formData.longitude}
                onChange={handleChange}
                placeholder="Lng"
                step="0.0001"
                required
              />
            </div>
          </div>
          <div className="form-group">
            <label>Total Residents</label>
            <input
              type="number"
              name="totalResidents"
              value={formData.totalResidents}
              onChange={handleChange}
              min="1"
              max="20"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label>Special Assistance</label>
          <select name="specialAssistance" value={formData.specialAssistance} onChange={handleChange}>
            <option value="None">None</option>
            <option value="Wheelchair">Wheelchair</option>
            <option value="Oxygen">Oxygen</option>
            <option value="Mobility">Mobility</option>
            <option value="Medical">Medical</option>
            <option value="Vision">Vision</option>
            <option value="Hearing">Hearing</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Pet Count</label>
            <input
              type="number"
              name="petCount"
              value={formData.petCount}
              onChange={handleChange}
              min="0"
              max="10"
            />
          </div>
          <div className="form-group">
            <label>Emergency Contact</label>
            <input
              type="text"
              name="emergencyContactName"
              value={formData.emergencyContactName}
              onChange={handleChange}
              placeholder="Contact name"
            />
            <input
              type="tel"
              name="emergencyContactPhone"
              value={formData.emergencyContactPhone}
              onChange={handleChange}
              placeholder="Phone number"
            />
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={formData.consentDataSharing}
              onChange={(e) =>
                setFormData({ ...formData, consentDataSharing: e.target.checked })
              }
            />
            Data sharing consent
          </label>
          <br />
          <label>
            <input
              type="checkbox"
              checked={formData.consentLocationSharing}
              onChange={(e) =>
                setFormData({ ...formData, consentLocationSharing: e.target.checked })
              }
            />
            Location sharing consent
          </label>
          <br />
          <label>
            <input
              type="checkbox"
              checked={formData.consentEmergencyAlerts}
              onChange={(e) =>
                setFormData({ ...formData, consentEmergencyAlerts: e.target.checked })
              }
            />
            Emergency alerts consent
          </label>
        </div>

        <button type="submit" className="btn-primary">Register Household</button>
      </form>
    </div>
  );
}

// Simple Household constructor - in production would use the Mongoose model
function Household(data) {
  this.householdId = data.householdId;
  this.buildingId = data.buildingId;
  this.location = data.location;
  this.totalResidents = data.totalResidents;
  this.residents = data.residents || [];
  this.specialAssistance = data.specialAssistance;
  this.petCount = data.petCount;
  this.emergencyContact = data.emergencyContact;
  this.consent = data.consent;
}

export default AddHouseholdForm;