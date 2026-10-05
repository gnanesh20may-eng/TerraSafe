const mongoose = require('mongoose');

const rescueObservationSchema = new mongoose.Schema({
  // Associated incident
  incident: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RescueIncident',
  },
  
  // Who made the observation
  observedBy: {
    type: String, // Rescue team ID or user ID
    required: true,
  },
  
  // Observation type
  observationType: {
    type: String,
    enum: ['LastKnownLocation', 'ImpactSnapshot', 'Bluetooth', 'Sound', 'Visual', 'TeamObservation'],
    required: true,
  },
  
  // Location of observation
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point',
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
    },
  },
  
  // Timestamp of observation
  observedAt: {
    type: Date,
    default: Date.now,
  },
  
  // Observation details
  details: {
    // For Bluetooth: RSSI, etc.
    rssi: Number,
    // For Sound: decibel level, etc.
    decibelLevel: Number,
    // For Visual: description
    description: String,
  },
  
  // Status
  status: {
    type: String,
    enum: ['Pending', 'Confirmed', 'Dismissed'],
    default: 'Pending',
  },
  
  // Associated survivor (if applicable)
  survivor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurvivorProfile',
  },
  
  // Notes
  notes: {
    type: String,
  },
}, {
  timestamps: true,
});

// Index for incident queries
rescueObservationSchema.index({ incident: 1 });

// Index for location queries
rescueObservationSchema.index({ location: '2dsphere' });

// Index for timestamp queries
rescueObservationSchema.index({ observedAt: -1 });

module.exports = mongoose.model('RescueObservation', rescueObservationSchema);