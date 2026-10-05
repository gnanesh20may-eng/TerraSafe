const mongoose = require('mongoose');

const bluetoothObservationSchema = new mongoose.Schema({
  // Associated observation (optional - can stand alone)
  observation: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RescueObservation',
  },
  
  // Rescue team or scanner device ID
  scannerId: {
    type: String,
    required: true,
    trim: true,
  },
  
  // Target device ID (anonymous)
  targetDeviceId: {
    type: String,
    trim: true,
  },
  
  // GPS location of scanner
  scannerLocation: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point',
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
    },
  },
  
  // RSSI value (Received Signal Strength Indicator)
  rssi: {
    type: Number, // dBm, typically -30 to -100
  },
  
  // Signal trend
  signalTrend: {
    type: String,
    enum: ['Getting Stronger', 'Getting Weaker', 'Stable', 'Unknown'],
    default: 'Unknown',
  },
  
  // Scan duration in seconds
  scanDuration: {
    type: Number,
    default: 0,
  },
  
  // Device capability
  deviceCapability: {
    type: String,
    enum: ['iOS', 'Android', 'Unknown'],
    default: 'Unknown',
  },
  
  // Observation quality
  quality: {
    type: String,
    enum: ['High', 'Medium', 'Low', 'Unreliable'],
    default: 'Medium',
  },
  
  // Environmental factors affecting signal
  environmentalFactors: {
    walls: Number, // estimated count
    metal: {
      type: Boolean,
      default: false,
    },
    water: {
      type: Boolean,
      default: false,
    },
  },
  
  // Timestamp
  recordedAt: {
    type: Date,
    default: Date.now,
  },
}, {
  timestamps: true,
});

// Index for survivor queries
bluetoothObservationSchema.index({ targetDeviceId: 1 });

// Index for scanner location queries
bluetoothObservationSchema.index({ 'scannerLocation.coordinates': '2dsphere' });

// Index for timestamp queries
bluetoothObservationSchema.index({ recordedAt: -1 });

// Method to determine signal trend
bluetoothObservationSchema.methods.determineTrend = function(previousRssi) {
  if (previousRssi === undefined) {
    this.signalTrend = 'Unknown';
    return this.save();
  }
  
  // If current RSSI is higher (less negative) than previous, it's getting stronger
  // RSSI is negative, so -50 > -70 means stronger signal
  if (this.rssi > previousRssi) {
    this.signalTrend = 'Getting Stronger';
  } else if (this.rssi < previousRssi) {
    this.signalTrend = 'Getting Weaker';
  } else {
    this.signalTrend = 'Stable';
  }
  
  return this.save();
};

module.exports = mongoose.model('BluetoothObservation', bluetoothObservationSchema);