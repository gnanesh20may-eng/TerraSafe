const mongoose = require('mongoose');

const emergencyContactSchema = new mongoose.Schema({
  // Associated survivor
  survivor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurvivorProfile',
  },
  
  // Contact name
  name: {
    type: String,
    required: true,
    trim: true,
  },
  
  // Relationship to survivor
  relationship: {
    type: String,
    trim: true,
  },
  
  // Phone number
  phone: {
    type: String,
    required: true,
    trim: true,
  },
  
  // Email (optional)
  email: {
    type: String,
    trim: true,
    lowercase: true,
  },
  
  // Permission levels
  permissions: {
    receiveAlerts: {
      type: Boolean,
      default: true,
    },
    receiveLocationUpdates: {
      type: Boolean,
      default: false, // Privacy: don't share location by default
    },
    canUpdateStatus: {
      type: Boolean,
      default: false,
    },
  },
  
  // Contact status
  isPrimary: {
    type: Boolean,
    default: false,
  },
  
  // Timestamp
  createdAt: {
    type: Date,
    default: Date.now,
  },
}, {
  timestamps: true,
});

module.exports = mongoose.model('EmergencyContact', emergencyContactSchema);