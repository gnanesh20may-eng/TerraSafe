const express = require('express');
const router = express.Router();
const ImpactSnapshot = require('../models/impactSnapshot');

// GET all impact snapshots
router.get('/', async (req, res) => {
  try {
    const snapshots = await ImpactSnapshot.find()
      .sort({ timestamp: -1 })
      .limit(50);
    res.json(snapshots);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET single impact snapshot
router.get('/:id', getImpactSnapshot, (req, res) => {
  res.json(res.impactSnapshot);
});

// CREATE impact snapshot
router.post('/', async (req, res) => {
  try {
    const snapshotData = {
      snapshotId: `IS-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
      location: req.body.location,
      timestamp: req.body.timestamp || new Date(),
      deviceId: req.body.deviceId,
      survivorId: req.body.survivorId,
      batteryPercentage: req.body.batteryPercentage,
      gpsAccuracy: req.body.gpsAccuracy,
      accelerometer: req.body.accelerometer,
      gyroscope: req.body.gyroscope,
      activityState: req.body.activityState,
    };
    
    const snapshot = await ImpactSnapshot.createSnapshot(snapshotData);
    res.status(201).json(snapshot);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// GET snapshots by survivor
router.get('/survivor/:survivorId', async (req, res) => {
  try {
    const snapshots = await ImpactSnapshot.find({ survivor: req.params.survivorId })
      .sort({ timestamp: -1 });
    res.json(snapshots);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// MARK user response
router.patch('/:id/response', getImpactSnapshot, async (req, res) => {
  try {
    await res.impactSnapshot.markUserResponse(req.body.response);
    res.json(res.impactSnapshot);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// MARK as uploaded
router.patch('/:id/upload', getImpactSnapshot, async (req, res) => {
  try {
    await res.impactSnapshot.markAsUploaded();
    res.json(res.impactSnapshot);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

module.exports = router;