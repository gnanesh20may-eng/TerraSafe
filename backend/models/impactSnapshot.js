const mongoose = require('mongoose');

const impactSnapshotSchema = new mongoose.Schema({
  // Unique ID for the snapshot
  snapshotId: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  
  // Associated survivor/user
  survivor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurvivorProfile',
  },
  
  // GPS location at time of impact
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point',
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
      required: true,
    },
  },
  
  // Timestamp of the event
  timestamp: {
    type: Date,
    required: true,
  },
  
  // Device information
  deviceId: {
    type: String,
    trim: true,
  },
  
  // Survivor ID (anonymous)
  survivorId: {
    type: String,
    trim: true,
  },
  
  // Battery percentage at time of event
  batteryPercentage: {
    type: Number,
    min: 0,
    max: 100,
    required: true,
  },
  
  // GPS accuracy at time of event
  gpsAccuracy: {
    type: Number, // in meters
  },
  
  // Accelerometer event data
  accelerometer: {
    x: Number,
    y: Number,
    z: Number,
    magnitude: Number,
    eventType: {
      type: String,
      enum: ['Impact', 'AbruptMovement', 'SuddenStop', 'FreeFall', 'Other'],
    },
  },
  
  // Gyroscope information if available
  gyroscope: {
    x: Number,
    y: Number,
    z: Number,
    available: {
      type: Boolean,
      default: false,
    },
  },
  
  // Current activity/movement state
  activityState: {
    type: String,
    enum: ['Still', 'Walking', 'Running', 'Vehicle', 'Falling', 'Unknown'],
    default: 'Unknown',
  },
  
  // User response status
  userResponse: {
    type: String,
    enum: ['IM_SAFE', 'NEEDS_HELP', 'NO_RESPONSE', 'ACKNOWLEDGED'],
    default: 'NO_RESPONSE',
  },
  
  // Event status
  eventStatus: {
    type: String,
    enum: ['Active', 'Uploaded', 'Acknowledged', 'Resolved'],
    default: 'Active',
  },
  
  // Associated landslide event
  landslideEvent: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RescueIncident',
  },
  
  // Evidence combination
  evidence: {
    rainfall: {
      type: Number, // mm/hour
    },
    terrainType: {
      type: String,
    },
    soilMoisture: {
      type: Number, // percentage
    },
  },
  
  // Privacy - anonymized data
  anonymized: {
    type: Boolean,
    default: true,
  },
  
  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now,
  },
}, {
  timestamps: true,
});

// Index for geospatial queries
impactSnapshotSchema.index({ location: '2dsphere' });

// Index for timestamp queries
impactSnapshotSchema.index({ timestamp: -1 });

// Method to mark user response
impactSnapshotSchema.methods.markUserResponse = function(response) {
  this.userResponse = response;
  return this.save();
};

// Method to mark event as uploaded
impactSnapshotSchema.methods.markAsUploaded = function() {
  this.eventStatus = 'Uploaded';
  return this.save();
};

// Static method to create a new impact snapshot
impactSnapshotSchema.statics.createSnapshot = function(data) {
  const snapshot = new this({
    snapshotId: `IS-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
    location: data.location,
    timestamp: data.timestamp || new Date(),
    deviceId: data.deviceId,
    survivorId: data.survivorId,
    batteryPercentage: data.batteryPercentage,
    gpsAccuracy: data.gpsAccuracy,
    accelerometer: data.accelerometer,
    gyroscope: data.gyroscope,
    activityState: data.activityState,
  });
  return snapshot.save();
};

module.exports = mongoose.model('ImpactSnapshot', impactSnapshotSchema);