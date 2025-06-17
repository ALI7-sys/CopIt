'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { MarketplaceProduct, ParseResult } from '@/types/marketplace';

interface MarketplaceContextType {
  products: MarketplaceProduct[];
  addProducts: (result: ParseResult) => void;
  removeProduct: (productId: string) => void;
  updateProduct: (productId: string, updates: Partial<MarketplaceProduct>) => void;
  clearProducts: () => void;
  stats: {
    total: number;
    backmarket: number;
    newegg: number;
  };
}

const MarketplaceContext = createContext<MarketplaceContextType | undefined>(undefined);

export function MarketplaceProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [products, setProducts] = useState<MarketplaceProduct[]>([]);

  const addProducts = useCallback((result: ParseResult) => {
    setProducts(prevProducts => {
      // Create a map of existing products for quick lookup
      const existingProducts = new Map(prevProducts.map(p => [p.id, p]));
      
      // Add new products, overwriting existing ones with the same ID
      result.products.forEach(product => {
        existingProducts.set(product.id, product);
      });

      return Array.from(existingProducts.values());
    });
  }, []);

  const removeProduct = useCallback((productId: string) => {
    setProducts(prevProducts => prevProducts.filter(p => p.id !== productId));
  }, []);

  const updateProduct = useCallback((productId: string, updates: Partial<MarketplaceProduct>) => {
    setProducts(prevProducts =>
      prevProducts.map(product =>
        product.id === productId ? { ...product, ...updates } : product
      )
    );
  }, []);

  const clearProducts = useCallback(() => {
    setProducts([]);
  }, []);

  const stats = {
    total: products.length,
    backmarket: products.filter(p => p.marketplace === 'backmarket').length,
    newegg: products.filter(p => p.marketplace === 'newegg').length,
  };

  const value = {
    products,
    addProducts,
    removeProduct,
    updateProduct,
    clearProducts,
    stats,
  };

  return (
    <MarketplaceContext.Provider value={value}>
      {children}
    </MarketplaceContext.Provider>
  );
}

export function useMarketplace(): MarketplaceContextType {
  const context = useContext(MarketplaceContext);
  if (context === undefined) {
    throw new Error('useMarketplace must be used within a MarketplaceProvider');
  }
  return context;
} 