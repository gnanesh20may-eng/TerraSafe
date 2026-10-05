const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  // Auth identifiers
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true,
  },
  
  password: {
    type: String,
    required: true,
  },
  
  role: {
    type: String,
    enum: ['citizen', 'rescueWorker', 'rescueCoordinator', 'administrator'],
    default: 'citizen',
  },
  
  // Profile information
  name: {
    type: String,
    trim: true,
  },
  
  // Consent
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
  
  // On-call status for rescue workers
  onCall: {
    type: Boolean,
    default: false,
  },
  
  // Active incident assignment
  activeIncident: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RescueIncident',
  },
  
  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now,
  },
  lastLogin: {
    type: Date,
  },
}, {
  timestamps: true,
});

// Method to check permissions
userSchema.methods.hasPermission = function(permission) {
  const permissionsByRole = {
    citizen: ['viewRescueMap', 'submitImpactSnapshot', 'viewOwnProfile'],
    rescueWorker: [
      'viewRescueMap',
      'submitImpactSnapshot',
      'updateSurvivorStatus',
      'recordFinding',
      'guideRescuer',
    ],
    rescueCoordinator: [
      'viewRescueMap',
      'manageIncidents',
      'updatePopulationCounts',
      'assignTeams',
      'viewAllData',
    ],
    administrator: ['allPermissions'],
  };
  
  const rolePermissions = permissionsByRole[this.role] || [];
  
  // Administrator has all permissions
  if (this.role === 'administrator') return true;
  
  return rolePermissions.includes(permission);
};

// Method to generate auth token
userSchema.methods.generateAuthToken = function() {
  const secret = process.env.JWT_SECRET || 'rescue-secret-key';
  return jwt.sign(
    { userId: this._id, role: this.role },
    secret,
    { expiresIn: '24h' }
  );
};

module.exports = mongoose.model('User', userSchema);