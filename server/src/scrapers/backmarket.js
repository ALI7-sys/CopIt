const puppeteer = require('puppeteer');
const { logger } = require('../config/logger');
const Product = require('../models/product');

class BackmarketScraper {
  constructor() {
    this.baseUrl = process.env.BACKMARKET_BASE_URL || 'https://www.backmarket.com';
    this.categories = [
      { name: 'Smartphones', url: '/us/en-us/c/smartphones' },
      { name: 'Laptops', url: '/us/en-us/c/laptops' },
      { name: 'Tablets', url: '/us/en-us/c/tablets' }
    ];
  }

  async initialize() {
    this.browser = await puppeteer.launch({
      headless: process.env.PUPPETEER_HEADLESS === 'true',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async scrapeProduct(url) {
    try {
      const page = await this.browser.newPage();
      await page.goto(url, { waitUntil: 'networkidle0' });

      const product = await page.evaluate(() => {
        const getPrice = () => {
          const priceElement = document.querySelector('[data-test="price"]');
          if (!priceElement) return null;
          const price = priceElement.innerText.replace(/[^0-9.]/g, '');
          return parseFloat(price);
        };

        const getOriginalPrice = () => {
          const priceElement = document.querySelector('[data-test="original-price"]');
          if (!priceElement) return null;
          const price = priceElement.innerText.replace(/[^0-9.]/g, '');
          return parseFloat(price);
        };

        const getImages = () => {
          const images = [];
          document.querySelectorAll('[data-test="product-image"]').forEach(img => {
            if (img.src) images.push(img.src);
          });
          return images;
        };

        const getSpecs = () => {
          const specs = new Map();
          document.querySelectorAll('[data-test="specs-list"] li').forEach(spec => {
            const [key, value] = spec.innerText.split(':').map(s => s.trim());
            if (key && value) specs.set(key, value);
          });
          return Object.fromEntries(specs);
        };

        return {
          name: document.querySelector('[data-test="product-title"]')?.innerText.trim(),
          price: getPrice(),
          originalPrice: getOriginalPrice(),
          description: document.querySelector('[data-test="product-description"]')?.innerText.trim(),
          images: getImages(),
          brand: document.querySelector('[data-test="product-brand"]')?.innerText.trim(),
          specifications: getSpecs(),
          stock: document.querySelector('[data-test="add-to-cart"]') ? 1 : 0
        };
      });

      if (!product.name || !product.price) {
        throw new Error('Required product data missing');
      }

      product.source = 'Backmarket';
      product.sourceUrl = url;
      product.sourceId = url.split('/').pop().split('?')[0];

      await page.close();
      return product;
    } catch (error) {
      logger.error(`Error scraping product from ${url}:`, error);
      throw error;
    }
  }

  async scrapeCategory(categoryUrl, limit = 10) {
    try {
      const page = await this.browser.newPage();
      await page.goto(`${this.baseUrl}${categoryUrl}`, { waitUntil: 'networkidle0' });

      const productLinks = await page.evaluate((limit) => {
        const links = [];
        document.querySelectorAll('[data-test="product-card"] a').forEach(link => {
          if (links.length < limit && link.href) {
            links.push(link.href);
          }
        });
        return links;
      }, limit);

      await page.close();

      const products = [];
      for (const link of productLinks) {
        try {
          const product = await this.scrapeProduct(link);
          products.push(product);
        } catch (error) {
          logger.error(`Error scraping product ${link}:`, error);
          continue;
        }
      }

      return products;
    } catch (error) {
      logger.error(`Error scraping category ${categoryUrl}:`, error);
      throw error;
    }
  }

  async scrapeAndSave() {
    try {
      await this.initialize();

      for (const category of this.categories) {
        logger.info(`Scraping category: ${category.name}`);
        
        const products = await this.scrapeCategory(category.url);
        
        for (const productData of products) {
          try {
            // Update existing product or create new one
            await Product.findOneAndUpdate(
              { source: 'Backmarket', sourceId: productData.sourceId },
              { 
                ...productData,
                category: category.name,
                updatedAt: Date.now()
              },
              { upsert: true, new: true }
            );
          } catch (error) {
            logger.error(`Error saving product ${productData.name}:`, error);
            continue;
          }
        }

        logger.info(`Completed scraping ${products.length} products from ${category.name}`);
      }
    } catch (error) {
      logger.error('Error in scraping process:', error);
    } finally {
      await this.close();
    }
  }
}

module.exports = BackmarketScraper; 