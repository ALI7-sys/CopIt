'use client';

import React, { useState } from 'react';
import { Product } from '@/types';
import { useCart } from '@/context/CartContext';

interface AddToCartButtonProps {
  product: Product;
  className?: string;
}

export default function AddToCartButton({ product, className = '' }: AddToCartButtonProps) {
  const { addItem } = useCart();
  const [isAdding, setIsAdding] = useState(false);

  const handleAddToCart = async () => {
    setIsAdding(true);
    try {
      addItem(product);
      // Optional: Add a success animation or notification here
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <button
      onClick={handleAddToCart}
      disabled={isAdding || product.stock === 0}
      className={`
        px-4 py-2 rounded-md font-medium transition-colors
        ${product.stock === 0
          ? 'bg-gray-300 cursor-not-allowed'
          : 'bg-blue-600 hover:bg-blue-700 text-white'
        }
        ${isAdding ? 'opacity-75 cursor-wait' : ''}
        ${className}
      `}
    >
      {product.stock === 0 ? (
        'Out of Stock'
      ) : isAdding ? (
        'Adding...'
      ) : (
        'Add to Cart'
      )}
    </button>
  );
} 