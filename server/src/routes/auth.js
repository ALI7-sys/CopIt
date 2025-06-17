const express = require('express');
const router = express.Router();
const { signup, login, logout, getMe } = require('../controllers/auth');
const { protect } = require('../middleware/auth');
const { authLimiter } = require('../middleware/rateLimiter');

// Apply rate limiting to auth routes
router.use(authLimiter);

// Public routes
router.post('/signup', signup);
router.post('/login', login);

// Protected routes
router.get('/logout', protect, logout);
router.get('/me', protect, getMe);

module.exports = router; 