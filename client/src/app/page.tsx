'use client';

import { useCart } from '../context/CartContext';
import { Cart } from '../components/Cart';
import { Product } from '@/types';

const sampleProduct: Product = {
  _id: '1',
  name: 'Sample Product',
  description: 'This is a sample product for testing the cart functionality.',
  price: 99.99,
  image: 'https://via.placeholder.com/150',
  stock: 10,
  category: 'Electronics',
  brand: 'Sample Brand',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

export default function Home() {
  const { addItem } = useCart();

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-luxury-gray-900">Welcome to CopIt</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="border border-luxury-gray-200 rounded-lg p-4 bg-white shadow-sm">
          <h2 className="text-xl font-semibold mb-4 text-luxury-gray-900">Sample Product</h2>
          <p className="text-luxury-gray-600 mb-4">{sampleProduct.description}</p>
          <p className="text-lg font-bold mb-4 text-luxury-gray-900">${sampleProduct.price}</p>
          <button
            onClick={() => addItem(sampleProduct)}
            className="bg-luxury-gray-700 text-white px-4 py-2 rounded hover:bg-luxury-gray-800 transition-colors"
          >
            Add to Cart
          </button>
        </div>

        <div className="border border-luxury-gray-200 rounded-lg bg-white shadow-sm">
          <Cart />
        </div>
      </div>
    </main>
  );
} 