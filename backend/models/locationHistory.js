const mongoose = require('mongoose');

const locationHistorySchema = new mongoose.Schema({
  // Associated survivor
  survivor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurvivorProfile',
    required: true,
  },
  
  // GPS location
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
  
  // GPS accuracy
  gpsAccuracy: {
    type: Number, // meters
  },
  
  // Timestamp
  timestamp: {
    type: Date,
    required: true,
  },
  
  // Activity state at this location
  activityState: {
    type: String,
    enum: ['Still', 'Walking', 'Running', 'Vehicle', 'Falling', 'Unknown'],
    default: 'Unknown',
  },
  
  // Battery level at this location
  batteryLevel: {
    type: Number,
    min: 0,
    max: 100,
  },
  
  // Source of location (GPS, network, etc.)
  locationSource: {
    type: String,
    enum: ['GPS', 'Network', 'Passive', 'LastKnown'],
    default: 'GPS',
  },
}, {
  timestamps: true,
});

// Index for geospatial queries
locationHistorySchema.index({ location: '2dsphere' });

// Index for timestamp queries
locationHistorySchema.index({ timestamp: -1 });

// Method to add a location point
locationHistorySchema.methods.addLocation = function(locationData) {
  this.location = locationData.location;
  this.gpsAccuracy = locationData.gpsAccuracy;
  this.timestamp = locationData.timestamp || new Date();
  this.activityState = locationData.activityState;
  if (locationData.batteryLevel !== undefined) this.batteryLevel = locationData.batteryLevel;
  return this.save();
};

module.exports = mongoose.model('LocationHistory', locationHistorySchema);