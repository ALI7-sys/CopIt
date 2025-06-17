export interface BaseProduct {
  id: string;
  name: string;
  price: number;
  description: string;
  image: string;
  category: string;
  stock: number;
  condition: string;
  seller: string;
  marketplace: 'backmarket' | 'newegg';
  url: string;
  createdAt: string;
  updatedAt: string;
}

export interface BackmarketProduct extends BaseProduct {
  marketplace: 'backmarket';
  warranty: string;
  refurbishedGrade: 'Excellent' | 'Good' | 'Fair';
  originalPrice: number;
  discount: number;
}

export interface NeweggProduct extends BaseProduct {
  marketplace: 'newegg';
  brand: string;
  model: string;
  sku: string;
  shipping: {
    price: number;
    method: string;
    estimatedDays: number;
  };
}

export type MarketplaceProduct = BackmarketProduct | NeweggProduct;

export interface ParseResult {
  products: MarketplaceProduct[];
  errors: string[];
  stats: {
    total: number;
    valid: number;
    invalid: number;
    backmarket: number;
    newegg: number;
  };
} 