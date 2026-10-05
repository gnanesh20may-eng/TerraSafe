const mongoose = require('mongoose');

const householdSchema = new mongoose.Schema({
  // Household ID - auto-generated or manual
  householdId: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  
  // House/building ID
  buildingId: {
    type: String,
    required: true,
    trim: true,
  },
  
  // GPS location
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point',
    },
    coordinates: {
      type: [Number],
      required: true, // [longitude, latitude]
    },
  },
  
  // Number of residents
  totalResidents: {
    type: Number,
    required: true,
    min: 1,
  },
  
  // Resident IDs - array of resident/survivor IDs
  residentIds: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurvivorProfile',
  }],
  
  // Resident details - name/alias and age category
  residents: [{
    name: {
      type: String,
      trim: true,
    },
    alias: {
      type: String,
      trim: true,
    },
    ageCategory: {
      type: String,
      enum: ['Child', 'Adult', 'Elder'],
    },
    gender: {
      type: String,
      enum: ['Male', 'Female', 'Other'],
    },
  }],
  
  // Optional special assistance requirement
  specialAssistance: {
    type: String,
    enum: ['None', 'Wheelchair', 'Oxygen', 'Mobility', 'Medical', 'Vision', 'Hearing', 'Other'],
    default: 'None',
  },
  
  // Optional pet count
  petCount: {
    type: Number,
    default: 0,
    min: 0,
  },
  
  // Emergency contact
  emergencyContact: {
    name: {
      type: String,
      trim: true,
    },
    phone: {
      type: String,
    },
    relationship: {
      type: String,
      trim: true,
    },
  },
  
  // Consent/preferences
  consent: {
    dataSharing: {
      type: Boolean,
      default: false,
    },
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
  
  // Status
  status: {
    type: String,
    enum: ['Active', 'Inactive', 'Archived'],
    default: 'Active',
  },
}, {
  timestamps: true,
});

// Index for geospatial queries
householdSchema.index({ location: '2dsphere' });

// Virtual for expected population calculation
householdSchema.virtual('expectedPopulation').get(function() {
  // Count confirmed safe + confirmed rescued = remaining calculation
  // This is computed dynamically based on survivor statuses
  return this.residents.length;
});

// Method to add a resident
householdSchema.methods.addResident = function(residentData) {
  this.residents.push(residentData);
  this.totalResidents = this.residents.length;
  return this.save();
};

// Method to mark a resident as safe
householdSchema.methods.markResidentSafe = function(residentId) {
  const resident = this.residents.find(r => r._id.toString() === residentId);
  if (resident) {
    resident.status = 'SAFE';
  }
  return this.save();
};

// Method to mark a resident as rescued
householdSchema.methods.markResidentRescued = function(residentId) {
  const resident = this.residents.find(r => r._id.toString() === residentId);
  if (resident) {
    resident.status = 'RESCUED';
  }
  return this.save();
};

// Method to get unaccounted people count
householdSchema.methods.getUnaccountedCount = function() {
  const safeCount = this.residents.filter(r => r.status === 'SAFE').length;
  const rescuedCount = this.residents.filter(r => r.status === 'RESCUED').length;
  return this.totalResidents - safeCount - rescuedCount;
};

module.exports = mongoose.model('Household', householdSchema);