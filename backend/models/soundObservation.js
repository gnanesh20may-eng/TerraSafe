const mongoose = require('mongoose');

const soundObservationSchema = new mongoose.Schema({
  // Associated observation (optional)
  observation: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RescueObservation',
  },
  
  // Rescue team or user ID
  observedBy: {
    type: String,
    required: true,
    trim: true,
  },
  
  // GPS location of the observation point
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
  
  // Decibel level
  decibelLevel: {
    type: Number, // dB SPL
    min: 0,
    max: 140,
  },
  
  // Beacon pattern detection
  beaconDetected: {
    type: Boolean,
    default: false,
  },
  
  // Beacon interval if detected
  beaconInterval: {
    type: Number, // seconds
  },
  
  // Trend
  signalTrend: {
    type: String,
    enum: ['Getting Louder', 'Getting Quieter', 'Stable', 'Unknown'],
    default: 'Unknown',
  },
  
  // Environmental notes
  environmentalNotes: {
    type: String,
  },
  
  // Timestamp
  recordedAt: {
    type: Date,
    default: Date.now,
  },
}, {
  timestamps: true,
});

// Index for location queries
soundObservationSchema.index({ location: '2dsphere' });

// Index for timestamp queries
soundObservationSchema.index({ recordedAt: -1 });

module.exports = mongoose.model('SoundObservation', soundObservationSchema);