const mongoose = require('mongoose');

const rescueFindingSchema = new mongoose.Schema({
  // Associated incident
  incident: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RescueIncident',
  },
  
  // The survivor who was found
  survivor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurvivorProfile',
  },
  
  // Who found the survivor
  foundBy: {
    type: String, // Rescue team ID
  },
  
  // GPS location where found
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
  
  // Status of the finding
  status: {
    type: String,
    enum: ['FOUND', 'RESCUED', 'SAFE', 'INJURED', 'TRANSFERRED'],
    default: 'FOUND',
  },
  
  // Time of finding
  foundAt: {
    type: Date,
    default: Date.now,
  },
  
  // Rescue team ID
  rescueTeamId: {
    type: String,
    trim: true,
  },
  
  // Notes
  notes: {
    type: String,
  },
  
  // Optional photo reference
  photoUrl: {
    type: String,
  },
  
  // Vital signs if available
  vitalSigns: {
    temperature: Number,
    heartRate: Number,
    breathing: String,
  },
}, {
  timestamps: true,
});

// Index for incident queries
rescueFindingSchema.index({ incident: 1 });

// Index for survivor queries
rescueFindingSchema.index({ survivor: 1 });

// Index for status queries
rescueFindingSchema.index({ status: 1 });

// Index for timestamp queries
rescueFindingSchema.index({ foundAt: -1 });

module.exports = mongoose.model('RescueFinding', rescueFindingSchema);