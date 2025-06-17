const express = require('express');
const router = express.Router();
const { protect, authorize } = require('../middleware/auth');
const Product = require('../models/product');
const { AppError } = require('../middleware/errorHandler');

// Get all products with filtering, sorting, and pagination
router.get('/', async (req, res, next) => {
  try {
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 10;
    const startIndex = (page - 1) * limit;

    // Build query
    let query = Product.find();

    // Filter by category
    if (req.query.category) {
      query = query.where('category').equals(req.query.category);
    }

    // Filter by brand
    if (req.query.brand) {
      query = query.where('brand').equals(req.query.brand);
    }

    // Filter by price range
    if (req.query.minPrice || req.query.maxPrice) {
      const priceFilter = {};
      if (req.query.minPrice) priceFilter.$gte = parseFloat(req.query.minPrice);
      if (req.query.maxPrice) priceFilter.$lte = parseFloat(req.query.maxPrice);
      query = query.where('price').equals(priceFilter);
    }

    // Search by name or description
    if (req.query.search) {
      query = query.or([
        { name: { $regex: req.query.search, $options: 'i' } },
        { description: { $regex: req.query.search, $options: 'i' } }
      ]);
    }

    // Sort
    if (req.query.sort) {
      const sortBy = req.query.sort.split(',').join(' ');
      query = query.sort(sortBy);
    } else {
      query = query.sort('-createdAt');
    }

    // Execute query with pagination
    const products = await query.skip(startIndex).limit(limit);
    const total = await Product.countDocuments(query.getQuery());

    res.status(200).json({
      success: true,
      count: products.length,
      total,
      totalPages: Math.ceil(total / limit),
      currentPage: page,
      data: products
    });
  } catch (error) {
    next(error);
  }
});

// Get single product
router.get('/:id', async (req, res, next) => {
  try {
    const product = await Product.findById(req.params.id);

    if (!product) {
      return next(new AppError('Product not found', 404));
    }

    res.status(200).json({
      success: true,
      data: product
    });
  } catch (error) {
    next(error);
  }
});

// Create new product (Admin only)
router.post('/', protect, authorize('admin'), async (req, res, next) => {
  try {
    const product = await Product.create(req.body);

    res.status(201).json({
      success: true,
      data: product
    });
  } catch (error) {
    next(error);
  }
});

// Update product (Admin only)
router.put('/:id', protect, authorize('admin'), async (req, res, next) => {
  try {
    const product = await Product.findByIdAndUpdate(
      req.params.id,
      req.body,
      {
        new: true,
        runValidators: true
      }
    );

    if (!product) {
      return next(new AppError('Product not found', 404));
    }

    res.status(200).json({
      success: true,
      data: product
    });
  } catch (error) {
    next(error);
  }
});

// Delete product (Admin only)
router.delete('/:id', protect, authorize('admin'), async (req, res, next) => {
  try {
    const product = await Product.findByIdAndDelete(req.params.id);

    if (!product) {
      return next(new AppError('Product not found', 404));
    }

    res.status(200).json({
      success: true,
      data: {}
    });
  } catch (error) {
    next(error);
  }
});

// Add product rating
router.post('/:id/ratings', protect, async (req, res, next) => {
  try {
    const product = await Product.findById(req.params.id);

    if (!product) {
      return next(new AppError('Product not found', 404));
    }

    // Check if user already rated
    const alreadyRated = product.ratings.find(
      rating => rating.user.toString() === req.user._id.toString()
    );

    if (alreadyRated) {
      return next(new AppError('Product already rated', 400));
    }

    const rating = {
      user: req.user._id,
      rating: req.body.rating,
      review: req.body.review
    };

    product.ratings.push(rating);
    await product.save();

    res.status(201).json({
      success: true,
      data: product
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router; 