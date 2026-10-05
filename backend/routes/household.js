const express = require('express');
const router = express.Router();
const Household = require('../models/household');

// GET all households
router.get('/', async (req, res) => {
  try {
    const households = await Household.find().sort({ createdAt: -1 });
    res.json(households);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET single household
router.get('/:id', getHousehold, (req, res) => {
  res.json(res.household);
});

// CREATE household
router.post('/', async (req, res) => {
  try {
    const household = new Household({
      householdId: req.body.householdId,
      buildingId: req.body.buildingId,
      location: {
        type: 'Point',
        coordinates: req.body.location.coordinates, // [longitude, latitude]
      },
      totalResidents: req.body.totalResidents,
      residents: req.body.residents,
      specialAssistance: req.body.specialAssistance,
      petCount: req.body.petCount,
      emergencyContact: req.body.emergencyContact,
      consent: req.body.consent,
    });
    
    const newHousehold = await household.save();
    res.status(201).json(newHousehold);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// UPDATE household
router.patch('/:id', getHousehold, async (req, res) => {
  try {
    if (req.body.location) {
      res.household.location = {
        type: 'Point',
        coordinates: req.body.location.coordinates,
      };
    }
    if (req.body.totalResidents !== undefined) {
      res.household.totalResidents = req.body.totalResidents;
    }
    if (req.body.specialAssistance !== undefined) {
      res.household.specialAssistance = req.body.specialAssistance;
    }
    if (req.body.emergencyContact !== undefined) {
      res.household.emergencyContact = req.body.emergencyContact;
    }
    if (req.body.consent !== undefined) {
      res.household.consent = req.body.consent;
    }
    res.household.updatedAt = Date.now();
    
    const updatedHousehold = await res.household.save();
    res.json(updatedHousehold);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// DELETE household
router.delete('/:id', getHousehold, async (req, res) => {
  try {
    await res.household.remove();
    res.json({ message: 'Household deleted' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET unaccounted count for a household
router.get('/:id/unaccounted', getHousehold, async (req, res) => {
  try {
    const unaccounted = res.household.getUnaccountedCount();
    res.json({ unaccounted });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;