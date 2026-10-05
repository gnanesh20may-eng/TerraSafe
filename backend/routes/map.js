const express = require('express');
const router = express.Router();
const Survivor = require('../models/survivor');
const ImpactSnapshot = require('../models/impactSnapshot');
const RescueObservation = require('../models/rescueObservation');
const BluetoothObservation = require('../models/bluetoothObservation');
const SoundObservation = require('../models/soundObservation');
const RescueFinding = require('../models/rescueFinding');
const RescueIncident = require('../models/rescueIncident');
const Household = require('../models/household');

// GET rescue map data - all relevant data for the rescue map
router.get('/', async (req, res) => {
  try {
    // Get active incidents
    const activeIncidents = await RescueIncident.find({ status: 'Active' });
    
    // Get all survivors with their statuses
    const allSurvivors = await Survivor.find();
    
    // Get recent impact snapshots
    const recentSnapshots = await ImpactSnapshot.find()
      .sort({ timestamp: -1 })
      .limit(20);
    
    // Get Bluetooth observations
    const bluetoothObservations = await BluetoothObservation.find()
      .sort({ recordedAt: -1 })
      .limit(30);
    
    // Get sound observations
    const soundObservations = await SoundObservation.find()
      .sort({ recordedAt: -1 })
      .limit(20);
    
    // Get rescue findings
    const rescueFindings = await RescueFinding.find()
      .sort({ foundAt: -1 })
      .limit(30);
    
    // Get households
    const households = await Household.find();
    
    res.json({
      activeIncidents,
      survivors: allSurvivors,
      impactSnapshots: recentSnapshots,
      bluetoothObservations,
      soundObservations,
      rescueFindings,
      households,
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET survivors for map with filters
router.get('/filter', async (req, res) => {
  try {
    const { status, priority, incidentId } = req.query;
    let query = {};
    
    if (status) query.status = status;
    if (priority) query.priority = priority;
    if (incidentId) query.incident = incidentId;
    
    const survivors = await Survivor.find(query);
    res.json(survivors);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET impact snapshots for area
router.get('/incident/:incidentId/snapshots', async (req, res) => {
  try {
    const snapshots = await ImpactSnapshot.find({
      landslideEvent: req.params.incidentId,
    })
      .sort({ timestamp: -1 });
    res.json(snapshots);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET Bluetooth observations for incident
router.get('/incident/:incidentId/bluetooth', async (req, res) => {
  try {
    const observations = await BluetoothObservation.find({
      'scannerLocation.coordinates': {
        $near: {
          $maxDistance: 5000,
          $geometry: {
            type: 'Point',
            coordinates: [], // Will be filled by client
          },
        },
      },
    }).limit(20);
    res.json(observations);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET rescue priority summary
router.get('/summary/priority', async (req, res) => {
  try {
    const critical = await Survivor.countDocuments({ priority: 'CRITICAL' });
    const high = await Survivor.countDocuments({ priority: 'HIGH' });
    const medium = await Survivor.countDocuments({ priority: 'MEDIUM' });
    const low = await Survivor.countDocuments({ priority: 'LOW' });
    
    const byStatus = await Survivor.aggregate([
      { $group: { _id: '$status', count: { $sum: 1 } } }
    ]);
    
    const summary = {
      byPriority: { CRITICAL: critical, HIGH: high, MEDIUM: medium, LOW: low },
      byStatus: byStatus.reduce((acc, curr) => {
        acc[curr._id] = curr.count;
        return acc;
      }, {}),
    };
    
    res.json(summary);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;