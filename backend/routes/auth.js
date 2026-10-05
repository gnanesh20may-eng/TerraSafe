const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const User = require('../models/user'); // We'll create this

// In a full implementation, this would use proper authentication
// For now, we'll set up the structure

// GET current user (mock)
router.get('/me', (req, res) => {
  // In production, verify JWT token from header
  res.json({ 
    userId: 'user-123', 
    role: 'citizen', 
    name: 'Test User' 
  });
});

// Login (mock - would use real auth in production)
router.post('/login', (req, res) => {
  const { username, password } = req.body;
  // Would verify credentials against database
  if (username && password) {
    const token = jwt.sign(
      { userId: 'user-123', role: 'citizen' },
      process.env.JWT_SECRET || 'secret-key',
      { expiresIn: '24h' }
    );
    res.json({ token, user: { id: 'user-123', role: 'citizen', name: 'Test User' } });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});

// Register (mock)
router.post('/register', (req, res) => {
  const { name, email, password, role } = req.body;
  // Would hash password and save to database
  res.status(201).json({ message: 'User registered successfully' });
});

// GET roles/permissions
router.get('/roles', (req, res) => {
  res.json({
    roles: {
      citizen: {
        can: [
          'viewRescueMap',
          'submitImpactSnapshot',
          'viewOwnProfile',
        ],
      },
      rescueWorker: {
        can: [
          'viewRescueMap',
          'submitImpactSnapshot',
          'update SurvivorStatus',
          'recordFinding',
          'guideRescuer',
        ],
      },
      rescueCoordinator: {
        can: [
          'viewRescueMap',
          'manageIncidents',
          'updatePopulationCounts',
          'assignTeams',
          'viewAllData',
        ],
      },
      administrator: {
        can: [
          'allPermissions',
        ],
      },
    },
  });
});

module.exports = router;