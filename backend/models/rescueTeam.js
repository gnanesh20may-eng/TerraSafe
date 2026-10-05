const mongoose = require('mongoose');

const rescueTeamSchema = new mongoose.Schema({
  // Team ID
  teamId: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  
  // Team name
  name: {
    type: String,
    required: true,
    trim: true,
  },
  
  // Team leader
  teamLeader: {
    type: String,
    trim: true,
  },
  
  // Members
  members: [{
    name: {
      type: String,
      trim: true,
    },
    role: {
      type: String,
    },
    contact: {
      type: String,
    },
  }],
  
  // Vehicle/equipment
  vehicle: {
    type: String,
    trim: true,
  },
  
  // Communication devices
  communication: {
    type: String,
    trim: true,
  },
  
  // Current location
  currentLocation: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point',
    },
    coordinates: {
      type: [Number],
    },
  },
  
  // Active assignment
  activeIncident: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RescueIncident',
  },
  
  // Status
  status: {
    type: String,
    enum: ['Available', 'Assigned', 'Busy', 'Resolved'],
    default: 'Available',
  },
  
  // Shift information
  shiftStart: {
    type: Date,
  },
  shiftEnd: {
    type: Date,
  },
}, {
  timestamps: true,
});

// Index for incident queries
rescueTeamSchema.index({ activeIncident: 1 });

// Index for status queries
rescueTeamSchema.index({ status: 1 });

module.exports = mongoose.model('RescueTeam', rescueTeamSchema);