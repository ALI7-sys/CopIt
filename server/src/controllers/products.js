const Product = require('../models/Product');

// Mock data for development
const mockProducts = [
  {
    name: "MacBook Pro 16\" M2",
    description: "Latest MacBook Pro with M2 chip, 16GB RAM, 512GB SSD",
    price: 2499.99,
    category: "Computers",
    brand: "Apple",
    images: ["https://images.newegg.com/productimage/9SIA0ZX6VY1234.jpg"],
    stock: 10,
    source: "newegg",
    sourceUrl: "https://www.newegg.com/macbook-pro-16-m2",
    lastUpdated: new Date(),
    createdAt: new Date()
  },
  {
    name: "iPhone 15 Pro",
    description: "Latest iPhone with A17 Pro chip, 256GB storage",
    price: 999.99,
    category: "Smartphones",
    brand: "Apple",
    images: ["https://images.newegg.com/productimage/9SIA0ZX6VY5678.jpg"],
    stock: 15,
    source: "newegg",
    sourceUrl: "https://www.newegg.com/iphone-15-pro",
    lastUpdated: new Date(),
    createdAt: new Date()
  },
  {
    name: "Samsung Galaxy S23 Ultra",
    description: "Refurbished Samsung Galaxy S23 Ultra, Like New Condition",
    price: 799.99,
    category: "Smartphones",
    brand: "Samsung",
    images: ["https://images.backmarket.com/productimage/BM123456.jpg"],
    stock: 8,
    source: "backmarket",
    sourceUrl: "https://www.backmarket.com/samsung-galaxy-s23-ultra",
    lastUpdated: new Date(),
    createdAt: new Date()
  }
];

// @desc    Get all products
// @route   GET /api/products
// @access  Public
const getProducts = async (req, res) => {
  try {
    // In development, return mock data
    if (process.env.NODE_ENV === 'development') {
      return res.json(mockProducts);
    }

    // In production, fetch from database
    const products = await Product.find();
    res.json(products);
  } catch (err) {
    res.status(500).json({
      success: false,
      error: 'Server Error'
    });
  }
};

// @desc    Get single product
// @route   GET /api/products/:id
// @access  Public
const getProduct = async (req, res) => {
  try {
    // In development, return mock data
    if (process.env.NODE_ENV === 'development') {
      const product = mockProducts.find(p => p._id === req.params.id);
      if (!product) {
        return res.status(404).json({
          success: false,
          error: 'Product not found'
        });
      }
      return res.json(product);
    }

    // In production, fetch from database
    const product = await Product.findById(req.params.id);
    if (!product) {
      return res.status(404).json({
        success: false,
        error: 'Product not found'
      });
    }
    res.json(product);
  } catch (err) {
    res.status(500).json({
      success: false,
      error: 'Server Error'
    });
  }
};

// @desc    Create new product
// @route   POST /api/products
// @access  Private
const createProduct = async (req, res) => {
  try {
    const product = await Product.create(req.body);
    res.status(201).json(product);
  } catch (err) {
    res.status(400).json({
      success: false,
      error: err.message
    });
  }
};

// @desc    Update product
// @route   PUT /api/products/:id
// @access  Private
const updateProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    if (!product) {
      return res.status(404).json({
        success: false,
        error: 'Product not found'
      });
    }
    res.json(product);
  } catch (err) {
    res.status(400).json({
      success: false,
      error: err.message
    });
  }
};

// @desc    Delete product
// @route   DELETE /api/products/:id
// @access  Private
const deleteProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndDelete(req.params.id);
    if (!product) {
      return res.status(404).json({
        success: false,
        error: 'Product not found'
      });
    }
    res.json({ success: true });
  } catch (err) {
    res.status(400).json({
      success: false,
      error: err.message
    });
  }
};

module.exports = {
  getProducts,
  getProduct,
  createProduct,
  updateProduct,
  deleteProduct
}; 