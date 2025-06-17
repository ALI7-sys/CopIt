const puppeteer = require('puppeteer');
const Product = require('../models/Product');
const mongoose = require('mongoose');
require('dotenv').config();

const scrapeNewegg = async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu'
    ]
  });

  try {
    const page = await browser.newPage();
    
    // Set viewport and user agent
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');

    // Navigate to Newegg deals page
    await page.goto('https://www.newegg.com/promotions/newegg-deals', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    // Wait for product grid to load
    await page.waitForSelector('.product-grid', { timeout: 10000 });

    // Extract product data with enhanced information
    const products = await page.evaluate(() => {
      const items = document.querySelectorAll('.product-grid .product-item');
      return Array.from(items).map(item => {
        // Basic product info
        const name = item.querySelector('.product-title')?.textContent.trim();
        const priceElement = item.querySelector('.price-current');
        const price = priceElement?.textContent.trim();
        const image = item.querySelector('.product-img img')?.src;
        const url = item.querySelector('a')?.href;

        // Enhanced product info
        const ratingElement = item.querySelector('.rating');
        const rating = ratingElement ? {
          score: parseFloat(ratingElement.getAttribute('data-rating') || '0'),
          count: parseInt(ratingElement.querySelector('.rating-count')?.textContent || '0', 10)
        } : null;

        const shippingElement = item.querySelector('.shipping-info');
        const shipping = shippingElement ? {
          price: shippingElement.querySelector('.shipping-price')?.textContent.trim(),
          method: shippingElement.querySelector('.shipping-method')?.textContent.trim()
        } : null;

        const stockElement = item.querySelector('.stock-status');
        const stock = stockElement ? {
          status: stockElement.textContent.trim(),
          quantity: parseInt(stockElement.getAttribute('data-stock') || '0', 10)
        } : null;

        const discountElement = item.querySelector('.discount-badge');
        const discount = discountElement ? {
          percentage: discountElement.textContent.trim(),
          originalPrice: discountElement.getAttribute('data-original-price')
        } : null;

        // Extract category and brand from breadcrumbs or product info
        const category = item.querySelector('.product-category')?.textContent.trim();
        const brand = item.querySelector('.product-brand')?.textContent.trim();

        return {
          name,
          price: parseFloat(price?.replace(/[^0-9.]/g, '') || '0'),
          image,
          url,
          rating,
          shipping,
          stock,
          discount,
          category,
          brand,
          timestamp: new Date().toISOString()
        };
      }).filter(product => product.name && product.price > 0); // Filter out invalid products
    });

    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI);

    // Save products to database with enhanced error handling
    const savedProducts = [];
    const errors = [];

    for (const product of products) {
      try {
        if (product.name && product.price && product.image) {
          const savedProduct = await Product.findOneAndUpdate(
            { sourceUrl: product.url },
            {
              name: product.name,
              price: product.price,
              images: [product.image],
              source: 'newegg',
              sourceUrl: product.url,
              description: `Brand: ${product.brand || 'Unknown'}\nCategory: ${product.category || 'Unknown'}\nRating: ${product.rating?.score || 'N/A'} (${product.rating?.count || 0} reviews)\nShipping: ${product.shipping?.method || 'N/A'} - ${product.shipping?.price || 'N/A'}\nStock: ${product.stock?.status || 'Unknown'}\nDiscount: ${product.discount?.percentage || 'None'}`,
              category: product.category || 'Other',
              brand: product.brand || 'Unknown',
              stock: product.stock?.quantity || 0,
              lastUpdated: new Date()
            },
            { upsert: true, new: true }
          );
          savedProducts.push(savedProduct);
        }
      } catch (error) {
        errors.push({
          product: product.name,
          error: error.message
        });
      }
    }

    console.log(`Scraped ${products.length} products from Newegg`);
    console.log(`Successfully saved ${savedProducts.length} products`);
    if (errors.length > 0) {
      console.error('Errors during product saving:', errors);
    }

  } catch (error) {
    console.error('Error scraping Newegg:', error);
    throw error;
  } finally {
    await browser.close();
    await mongoose.disconnect();
  }
};

// Run scraper if called directly
if (require.main === module) {
  scrapeNewegg()
    .then(() => process.exit(0))
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = scrapeNewegg; 