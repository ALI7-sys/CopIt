require('dotenv').config();
const mongoose = require('mongoose');
const { logger } = require('../config/logger');
const NeweggScraper = require('./newegg');
const BackmarketScraper = require('./backmarket');

async function runScrapers() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    logger.info('Connected to MongoDB');

    // Run Newegg scraper
    logger.info('Starting Newegg scraper');
    const neweggScraper = new NeweggScraper();
    await neweggScraper.scrapeAndSave();
    logger.info('Completed Newegg scraping');

    // Run Backmarket scraper
    logger.info('Starting Backmarket scraper');
    const backmarketScraper = new BackmarketScraper();
    await backmarketScraper.scrapeAndSave();
    logger.info('Completed Backmarket scraping');

  } catch (error) {
    logger.error('Error running scrapers:', error);
  } finally {
    await mongoose.disconnect();
    logger.info('Disconnected from MongoDB');
  }
}

// Run scrapers if called directly
if (require.main === module) {
  runScrapers();
}

module.exports = runScrapers; 