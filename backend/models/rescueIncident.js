const mongoose = require('mongoose');

const rescueIncidentSchema = new mongoose.Schema({
  // Incident ID
  incidentId: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  
  // Associated landslide prediction
  landslideEvent: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'PredictionResult',
  },
  
  // Incident name/identifier
  name: {
    type: String,
    required: true,
    trim: true,
  },
  
  // Description
  description: {
    type: String,
  },
  
  // Geographic extent - landslide polygon
  affectedArea: {
    type: {
      type: String,
      enum: ['Polygon'],
      default: 'Polygon',
    },
    coordinates: {
      type: [
        {
          type: [Number], // [longitude, latitude]
        },
      ],
      validate: {
        validator: function(coords) {
          return coords && coords.length >= 4; // Minimum polygon
        },
        message: 'Affected area must have polygon coordinates',
      },
    },
  },
  
  // Predicted risk zone (may differ from actual extent)
  predictedRiskZone: {
    type: {
      type: String,
      enum: ['Polygon'],
      default: 'Polygon',
    },
    coordinates: {
      type: [
        {
          type: [Number],
        },
      ],
    },
  },
  
  // Estimated affected population
  estimatedPopulation: {
    type: Number,
    default: 0,
  },
  
  // Confirmed safe people
  confirmedSafe: {
    type: Number,
    default: 0,
  },
  
  // Confirmed rescued people
  confirmedRescued: {
    type: Number,
    default: 0,
  },
  
  // Unaccounted people
  unaccountedPeople: {
    type: Number,
    default: 0,
  },
  
  // Active incident status
  status: {
    type: String,
    enum: ['Active', 'Resolved', 'Archived'],
    default: 'Active',
  },
  
  // Start and end timestamps
  startedAt: {
    type: Date,
    default: Date.now,
  },
  resolvedAt: {
    type: Date,
  },
  
  // Location centroid
  centroid: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point',
    },
    coordinates: {
      type: [Number],
    },
  },
  
  // Additional metadata
  metadata: {
    rainfall: {
      type: Number, // mm
    },
    soilType: {
      type: String,
    },
    terrainType: {
      type: String,
    },
    warningLevel: {
      type: String,
      enum: ['Low', 'Moderate', 'High', 'Critical'],
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
}, {
  timestamps: true,
});

// Index for status queries
rescueIncidentSchema.index({ status: 1 });

// Index for landslide event reference
rescueIncidentSchema.index({ landslideEvent: 1 });

// Method to update population counts
rescueIncidentSchema.methods.updatePopulationCounts = function() {
  // Recalculate based on survivor statuses
  if (this.survivors && this.survivors.length > 0) {
    const safeCount = this.survivors.filter(s => s.status === 'SAFE').length;
    const rescuedCount = this.survivors.filter(s => s.status === 'RESCUED').length;
    const unaccountedCount = this.survivors.filter(
      s => !['SAFE', 'RESCUED'].includes(s.status)
    ).length;
    
    this.confirmedSafe = safeCount;
    this.confirmedRescued = rescuedCount;
    this.unaccountedPeople = unaccountedCount;
    this.estimatedPopulation = this.survivors.length;
  }
  
  return this.save();
};

// Method to add a survivor to the incident
rescueIncidentSchema.methods.addSurvivor = function(survivorId) {
  // Ensure survivors array exists
  if (!this.survivors) this.survivors = [];
  
  // Add if not already present
  if (!this.survivors.includes(survivorId)) {
    this.survivors.push(survivorId);
  }
  
  return this.save();
};

module.exports = mongoose.model('RescueIncident', rescueIncidentSchema);