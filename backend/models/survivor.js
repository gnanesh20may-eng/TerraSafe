const mongoose = require('mongoose');

const survivorSchema = new mongoose.Schema({
  // Survivor ID - anonymous identifier
  survivorId: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  
  // Associated household
  household: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Household',
  },
  
  // Last known location
  lastKnownLocation: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point',
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
    },
    gpsAccuracy: {
      type: Number, // in meters
    },
  },
  
  // Last known timestamp
  lastLocationTimestamp: {
    type: Date,
  },
  
  // Last activity timestamp
  lastActivityTimestamp: {
    type: Date,
  },
  
  // Current status
  status: {
    type: String,
    enum: [
      'SAFE',      // Confirmed safe
      'NEEDS_HELP', // Needs help
      'UNACCOUNTED', // Unaccounted for
      'POSSIBLY_TRAPPED', // Possibly trapped
      'SIGNAL_DETECTED', // Device signal detected
      'RESCUED',    // Rescued
      'UNKNOWN',    // Unknown status
    ],
    default: 'UNACCOUNTED',
  },
  
  // Device availability
  deviceAvailability: {
    type: String,
    enum: ['Available', 'Unavailable', 'Unknown', 'Offline'],
    default: 'Unknown',
  },
  
  // Signal status (for Bluetooth/GPS)
  signalStatus: {
    type: String,
    enum: ['Strong', 'Weak', 'Intermittent', 'None', 'Unknown'],
    default: 'Unknown',
  },
  
  // Search confidence score
  searchConfidence: {
    type: Number, // 0-100
    default: 0,
  },
  
  // Priority level
  priority: {
    type: String,
    enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
    default: 'MEDIUM',
  },
  
  // Device information
  deviceId: {
    type: String,
    trim: true,
  },
  
  // Battery level if available
  batteryLevel: {
    type: Number, // 0-100
    min: 0,
    max: 100,
  },
  
  // Connectivity state
  connectivityState: {
    type: String,
    enum: ['Online', 'Offline', 'Limited', 'Unknown'],
    default: 'Unknown',
  },
  
  // Impact snapshot reference
  impactSnapshot: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'ImpactSnapshot',
  },
  
  // Landslide overlap status
  landslideOverlap: {
    type: Boolean,
    default: false,
  },
  
  // Building affected status
  buildingAffected: {
    type: Boolean,
    default: false,
  },
  
  // Special assistance needs
  specialNeeds: {
    type: String,
    enum: ['None', 'Mobility', 'Medical', 'Oxygen', 'Vision', 'Hearing', 'Wheelchair'],
    default: 'None',
  },
  
  // Pet information
  hasPets: {
    type: Boolean,
    default: false,
  },
  
  // Consent
  consent: {
    locationSharing: {
      type: Boolean,
      default: false,
    },
    emergencyAlerts: {
      type: Boolean,
      default: false,
    },
  },
  
  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Index for geospatial queries
survivorSchema.index({ lastKnownLocation: '2dsphere' });

// Index for status queries
survivorSchema.index({ status: 1 });

// Index for priority queries
survivorSchema.index({ priority: 1 });

// Method to update status and recalculate priority
survivorSchema.methods.updateStatus = function(newStatus, options = {}) {
  this.status = newStatus;
  
  // Update priority based on new status and other factors
  const priorityMap = {
    SAFE: 'LOW',
    UNACCOUNTED: 'HIGH',
    POSSIBLY_TRAPPED: 'CRITICAL',
    NEEDS_HELP: 'CRITICAL',
    SIGNAL_DETECTED: 'HIGH',
    RESCUED: 'LOW',
    UNKNOWN: 'MEDIUM',
  };
  
  this.priority = priorityMap[newStatus] || 'MEDIUM';
  
  // Adjust based on additional factors
  if (options.landslideOverlap) {
    this.priority = this.priority === 'LOW' ? 'HIGH' : this.priority;
  }
  if (options.noResponse) {
    this.priority = this.priority === 'LOW' ? 'HIGH' : this.priority;
  }
  if (options.deviceSignal) {
    this.priority = this.priority === 'LOW' ? 'MEDIUM' : this.priority;
  }
  
  return this.save();
};

// Method to calculate search confidence
survivorSchema.methods.calculateSearchConfidence = function() {
  let confidence = 0;
  let reasons = [];
  
  // Last GPS available
  if (this.lastKnownLocation && this.lastKnownLocation.coordinates) {
    confidence += 25;
    reasons.push('✓ Last GPS');
  }
  
  // Impact snapshot
  if (this.impactSnapshot) {
    confidence += 20;
    reasons.push('✓ Impact Snapshot');
  }
  
  // Household match
  if (this.household) {
    confidence += 20;
    reasons.push('✓ Household match');
  }
  
  // Bluetooth detected
  if (this.signalStatus === 'Strong' || this.signalStatus === 'Weak') {
    confidence += 15;
    reasons.push('✓ Bluetooth detected');
  }
  
  // Sound beacon detection
  // (would be checked separately)
  
  // Landslide extent overlap
  if (this.landslideOverlap) {
    confidence += 10;
    reasons.push('✓ Landslide extent');
  }
  
  // Building affected
  if (this.buildingAffected) {
    confidence += 10;
    reasons.push('✓ Building affected');
  }
  
  this.searchConfidence = Math.min(confidence, 100);
  return this.save();
};

// Virtual for time since last communication
survivorSchema.virtual('timeSinceLastCommunication').get function() {
  if (!this.lastLocationTimestamp) return 'Never';
  
  const diffMs = new Date() - new Date(this.lastLocationTimestamp);
  const diffMin = Math.floor(diffMs / 60000);
  
  if (diffMin < 1) return 'Less than a minute ago';
  if (diffMin < 60) return `${diffMin} minutes ago`;
  const diffHrs = Math.floor(diffMin / 60);
  if (diffHrs < 24) return `${diffHrs} hours ago`;
  const diffDays = Math.floor(diffHrs / 24);
  return `${diffDays} days ago`;
};

module.exports = mongoose.model('SurvivorProfile', survivorSchema);