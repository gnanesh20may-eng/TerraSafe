const express = require('express');
const router = express.Router();
const Survivor = require('../models/survivor');

// GET all survivors
router.get('/', async (req, res) => {
  try {
    const survivors = await Survivor.find().sort({ createdAt: -1 });
    res.json(survivors);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET single survivor
router.get('/:id', getSurvivor, (req, res) => {
  res.json(res.survivor);
});

// CREATE survivor
router.post('/', async (req, res) => {
  try {
    const survivor = new Survivor({
      survivorId: req.body.survivorId,
      household: req.body.household,
      lastKnownLocation: {
        type: 'Point',
        coordinates: req.body.lastKnownLocation?.coordinates,
      },
      lastLocationTimestamp: req.body.lastLocationTimestamp,
      status: req.body.status,
      deviceAvailability: req.body.deviceAvailability,
      signalStatus: req.body.signalStatus,
      priority: req.body.priority,
      deviceId: req.body.deviceId,
      batteryLevel: req.body.batteryLevel,
      connectivityState: req.body.connectivityState,
    });
    
    const newSurvivor = await survivor.save();
    
    // Also update the household's resident count
    if (req.body.household) {
      await Household.findByIdAndUpdate(req.body.household, {
        $push: { residentIds: newSurvivor._id }
      });
    }
    
    res.status(201).json(newSurvivor);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// UPDATE survivor
router.patch('/:id', getSurvivor, async (req, res) => {
  try {
    if (req.body.status) {
      res.survivor.status = req.body.status;
    }
    if (req.body.priority !== undefined) {
      res.survivor.priority = req.body.priority;
    }
    if (req.body.signalStatus !== undefined) {
      res.survivor.signalStatus = req.body.signalStatus;
    }
    if (req.body.deviceAvailability !== undefined) {
      res.survivor.deviceAvailability = req.body.deviceAvailability;
    }
    if (req.body.batteryLevel !== undefined) {
      res.survivor.batteryLevel = req.body.batteryLevel;
    }
    if (req.body.signalStatus !== undefined) {
      res.survivor.signalStatus = req.body.signalStatus;
    }
    if (req.body.landslideOverlap !== undefined) {
      res.survivor.landslideOverlap = req.body.landslideOverlap;
    }
    if (req.body.buildingAffected !== undefined) {
      res.survivor.buildingAffected = req.body.buildingAffected;
    }
    
    res.survivor.updatedAt = Date.now();
    
    // Recalculate search confidence
    await res.survivor.calculateSearchConfidence();
    
    const updatedSurvivor = await res.survivor.save();
    res.json(updatedSurvivor);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// GET survivor unaccounted count
router.get('/:id/unaccounted', async (req, res) => {
  try {
    // This would need household context
    // For now, return basic status
    res.json({ status: res.survivor.status });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Calculate search confidence
router.post('/:id/calculate-confidence', getSurvivor, async (req, res) => {
  try {
    await res.survivor.calculateSearchConfidence();
    const updatedSurvivor = await res.survivor.save();
    res.json(updatedSurvivor);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// GET survivors by status
router.get('/status/:status', async (req, res) => {
  try {
    const survivors = await Survivor.find({ status: req.params.status });
    res.json(survivors);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET survivors by priority
router.get('/priority/:priority', async (req, res) => {
  try {
    const survivors = await Survivor.find({ priority: req.params.priority });
    res.json(survivors);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get household survivors
router.get('/household/:householdId', async (req, res) => {
  try {
    const household = await Household.findById(req.params.householdId).populate('residentIds');
    res.json(household);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;