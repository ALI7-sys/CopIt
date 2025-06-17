'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Product } from '@/types/product';

export interface ProductCardProps {
  product: Product;
  onAddToCart: () => void;
}

export default function ProductCard({ product, onAddToCart }: ProductCardProps) {
  return (
    <div className="group relative bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <Link href={`/products/${product._id}`}>
        <div className="relative h-48">
          <Image
            src={product.image}
            alt={product.name}
            fill
            className="object-cover"
          />
        </div>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
          <p className="text-gray-600 text-sm mb-2">{product.description}</p>
          <div className="flex justify-between items-center">
            <span className="text-xl font-bold">${product.price}</span>
            <span className="text-sm text-gray-500">In Stock: {product.stock}</span>
          </div>
        </div>
      </Link>
      <div className="p-4 pt-0">
        <button
          onClick={onAddToCart}
          className="w-full bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
        >
          Add to Cart
        </button>
      </div>
    </div>
  );
} 