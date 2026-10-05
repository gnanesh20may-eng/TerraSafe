/**
 * Landslide Prediction + Rescue Intelligence Backend
 * 
 * This module extends the existing prediction application with post-landslide
 * rescue capabilities. It works alongside the existing prediction system rather
 * than replacing it.
 */

 const express = require('express');
 const mongoose = require('mongoose');
 const cors = require('cors');
 const helmet = require('helmet');
 const rateLimit = require('express-rate-limit');
 const mongoSanitize = require('express-mongo-sanitize');
 const xss = require('xss-clean');
 const hpp = require('hpp');
 const dotenv = require('dotenv');
 const fs = require('fs');
 const path = require('path');
 
 // Load environment variables
 dotenv.config();
 
 // Initialize Express
 const app = express();
 
 // Security middleware
 app.use(helmet());
 app.use(cors({
   origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
   credentials: true,
 }));
 app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
 app.use(mongoSanitize());
 app.use(xss());
 app.use(hpp());
 
 // Body parsing
 app.use(express.json({ limit: '10kb' }));
 app.use(express.urlencoded({ extended: true, limit: '10kb' }));
 
 // Connect to MongoDB
 mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/landslide-rescue', {
   useNewUrlParser: true,
   useUnifiedTopology: true,
 })
 .then(() => console.log('MongoDB connected'))
 .catch(err => console.error('MongoDB connection error:', err));
 
 // Import routes
 const predictionRoutes = require('./routes/prediction');
 const rescueRoutes = require('./routes/rescue');
 const householdRoutes = require('./routes/household');
 const survivorRoutes = require('./routes/survivor');
 const impactRoutes = require('./routes/impact');
 const mapRoutes = require('./routes/map');
 const authRoutes = require('./routes/auth');
 const userRoutes = require('./routes/user');
 
 // Use routes
 app.use('/api/predictions', predictionRoutes);
 app.use('/api/rescue', rescueRoutes);
 app.use('/api/households', householdRoutes);
 app.use('/api/survivors', survivorRoutes);
 app.use('/api/impacts', impactRoutes);
 app.use('/api/map', mapRoutes);
 app.use('/api/auth', authRoutes);
 app.use('/api/user', userRoutes);
 
 // Health check
 app.get('/health', (req, res) => {
   res.json({ status: 'ok', timestamp: new Date() });
 });
 
 // Serve static files in production
 if (process.env.NODE_ENV === 'production') {
   const buildPath = path.join(__dirname, '../frontend/build');
   if (fs.existsSync(buildPath)) {
     app.use(express.static(buildPath));
     app.get('*', (req, res) => {
       res.sendFile(path.join(buildPath, 'index.html'));
     });
   }
 }
 
 const PORT = process.env.PORT || 5000;
 app.listen(PORT, () => console.log(`Server running on port ${PORT}`));