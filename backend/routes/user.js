const express = require('express');
const router = express.Router();
const User = require('../models/user');

// GET current user profile
router.get('/me', async (req, res) => {
  try {
    // In a real app, verify JWT from header
    // For now, return a default user or the one from token
    const userId = req.query.userId || 'user-123';
    const user = await User.findOne({ username: userId });
    if (!user) {
      // Create a default user if none exists
      const newUser = new User({
        username: userId,
        role: 'citizen',
        name: 'Test User',
      });
      await newUser.save();
    }
    const foundUser = await User.findOne({ username: userId });
    res.json(foundUser);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET user by ID
router.get('/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id).select('-password');
    if (!user) return res.status(404).json({ message: 'User not found' });
    res.json(user);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// UPDATE user profile
router.patch('/:id', async (req, res) => {
  try {
    const updates = Object.keys(req.body).filter(
      key => key !== 'password' && key !== 'role'
    );
    const allowedUpdates = ['name', 'email', 'consent'];
    
    const isValidOperation = updates.every(update =>
      allowedUpdates.includes(update)
    );
    
    if (!isValidOperation) {
      return res.status(400).json({ message: 'Invalid updates' });
    }
    
    const user = await User.findByIdAndUpdate(req.params.id, { $set: req.body }, {
      new: true,
      runValidators: true,
    });
    
    if (!user) return res.status(404).json({ message: 'User not found' });
    res.json(user);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// GET available roles and permissions
router.get('/roles', (req, res) => {
  res.json({
    roles: {
      citizen: {
        description: 'Regular citizen',
        can: [
          'viewRescueMap',
          'submitImpactSnapshot',
          'viewOwnProfile',
          'submitSurvivalMode',
        ],
      },
      rescueWorker: {
        description: 'Rescue worker',
        can: [
          'viewRescueMap',
          'submitImpactSnapshot',
          'updateSurvivorStatus',
          'recordFinding',
          'guideRescuer',
          'scanBluetooth',
        ],
      },
      rescueCoordinator: {
        description: 'Rescue coordinator',
        can: [
          'viewRescueMap',
          'manageIncidents',
          'updatePopulationCounts',
          'assignTeams',
          'viewAllData',
          'resolveIncident',
        ],
      },
      administrator: {
        description: 'System administrator',
        can: ['allPermissions'],
      },
    },
  });
});

module.exports = router;