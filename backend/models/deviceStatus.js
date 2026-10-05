const mongoose = require('mongoose');

const deviceStatusSchema = new mongoose.Schema({
  // Associated survivor
  survivor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurvivorProfile',
    required: true,
  },
  
  // Battery level
  batteryLevel: {
    type: Number,
    min: 0,
    max: 100,
    default: 100,
  },
  
  // Connectivity state
  connectivityState: {
    type: String,
    enum: ['Online', 'Offline', 'Limited', 'AirplaneMode', 'Unknown'],
    default: 'Unknown',
  },
  
  // GPS state
  gpsState: {
    type: String,
    enum: ['Enabled', 'Disabled', 'Acquiring', 'Unknown'],
    default: 'Unknown',
  },
  
  // Last signal check
  lastSignalCheck: {
    type: Date,
    default: Date.now,
  },
  
  // Network type
  networkType: {
    type: String,
    enum: ['WiFi', 'Cellular', '5G', '4G', '3G', 'None', 'Unknown'],
    default: 'None',
  },
  
  // Device model (anonymous)
  deviceModel: {
    type: String,
    trim: true,
  },
  
  // OS version (anonymous)
  osVersion: {
    type: String,
    trim: true,
  },
  
  // Timestamp
  recordedAt: {
    type: Date,
    default: Date.now,
  },
}, {
  timestamps: true,
});

// Method to update battery and connectivity
deviceStatusSchema.methods.updateStatus = function(battery, connectivity, gpsState) {
  if (battery !== undefined) this.batteryLevel = battery;
  if (connectivity !== undefined) this.connectivityState = connectivity;
  if (gpsState !== undefined) this.gpsState = gpsState;
  this.lastSignalCheck = new Date();
  return this.save();
};

module.exports = mongoose.model('DeviceStatus', deviceStatusSchema);