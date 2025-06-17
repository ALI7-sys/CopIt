import Papa from 'papaparse';
import { MarketplaceProduct, BackmarketProduct, NeweggProduct, ParseResult } from '@/types/marketplace';

/**
 * Validates a product object based on its marketplace type
 */
const validateProduct = (product: any, marketplace: 'backmarket' | 'newegg'): string[] => {
  const errors: string[] = [];
  const requiredFields = ['id', 'name', 'price', 'description', 'image', 'category', 'stock'];

  // Check required fields
  requiredFields.forEach(field => {
    if (!product[field]) {
      errors.push(`Missing required field: ${field}`);
    }
  });

  // Validate price
  if (isNaN(Number(product.price)) || Number(product.price) < 0) {
    errors.push('Invalid price');
  }

  // Validate stock
  if (isNaN(Number(product.stock)) || Number(product.stock) < 0) {
    errors.push('Invalid stock quantity');
  }

  // Marketplace specific validations
  if (marketplace === 'backmarket') {
    if (!['Excellent', 'Good', 'Fair'].includes(product.refurbishedGrade)) {
      errors.push('Invalid refurbished grade');
    }
    if (isNaN(Number(product.originalPrice)) || Number(product.originalPrice) < 0) {
      errors.push('Invalid original price');
    }
  } else if (marketplace === 'newegg') {
    if (!product.brand || !product.model || !product.sku) {
      errors.push('Missing required Newegg fields');
    }
    if (!product.shipping?.price || !product.shipping?.method) {
      errors.push('Invalid shipping information');
    }
  }

  return errors;
};

/**
 * Transforms raw CSV data into a typed product object
 */
const transformProduct = (row: any, marketplace: 'backmarket' | 'newegg'): MarketplaceProduct => {
  const baseProduct = {
    id: row.id || String(Math.random()),
    name: row.name,
    price: Number(row.price),
    description: row.description,
    image: row.image,
    category: row.category,
    stock: Number(row.stock),
    condition: row.condition,
    seller: row.seller,
    marketplace,
    url: row.url,
    createdAt: row.createdAt || new Date().toISOString(),
    updatedAt: row.updatedAt || new Date().toISOString(),
  };

  if (marketplace === 'backmarket') {
    return {
      ...baseProduct,
      marketplace: 'backmarket',
      warranty: row.warranty,
      refurbishedGrade: row.refurbishedGrade,
      originalPrice: Number(row.originalPrice),
      discount: Number(row.discount),
    } as BackmarketProduct;
  } else {
    return {
      ...baseProduct,
      marketplace: 'newegg',
      brand: row.brand,
      model: row.model,
      sku: row.sku,
      shipping: {
        price: Number(row.shippingPrice),
        method: row.shippingMethod,
        estimatedDays: Number(row.shippingDays),
      },
    } as NeweggProduct;
  }
};

/**
 * Parses a CSV file from Backmarket or Newegg into typed product objects
 */
export const parseMarketplaceCSV = async (
  file: File | string,
  marketplace: 'backmarket' | 'newegg'
): Promise<ParseResult> => {
  const result: ParseResult = {
    products: [],
    errors: [],
    stats: {
      total: 0,
      valid: 0,
      invalid: 0,
      backmarket: 0,
      newegg: 0,
    },
  };

  try {
    // Parse CSV file
    const parseResult = await new Promise<Papa.ParseResult<any>>((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim().toLowerCase(),
        complete: resolve,
        error: reject,
      });
    });

    result.stats.total = parseResult.data.length;

    // Process each row
    parseResult.data.forEach((row) => {
      try {
        // Validate the row data
        const validationErrors = validateProduct(row, marketplace);
        
        if (validationErrors.length > 0) {
          result.errors.push(`Row ${result.stats.total - parseResult.data.length + 1}: ${validationErrors.join(', ')}`);
          result.stats.invalid++;
          return;
        }

        // Transform and add valid product
        const product = transformProduct(row, marketplace);
        result.products.push(product);
        result.stats.valid++;
        result.stats[marketplace]++;

      } catch (error) {
        result.errors.push(`Error processing row: ${error instanceof Error ? error.message : 'Unknown error'}`);
        result.stats.invalid++;
      }
    });

  } catch (error) {
    result.errors.push(`Failed to parse CSV: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }

  return result;
};

/**
 * Example usage:
 * 
 * const file = new File(['...'], 'products.csv', { type: 'text/csv' });
 * const result = await parseMarketplaceCSV(file, 'backmarket');
 * 
 * if (result.errors.length > 0) {
 *   console.error('Parsing errors:', result.errors);
 * }
 * 
 * console.log(`Successfully parsed ${result.stats.valid} products`);
 * console.log(`Found ${result.stats.backmarket} Backmarket products`);
 * console.log(`Found ${result.stats.newegg} Newegg products`);
 */ 