'use client';

import React from 'react';
import { useCart } from '@/context/CartContext';
import Image from 'next/image';
import { CartItem } from '@/types/cart';

export const Cart: React.FC = () => {
  const { items, removeItem, updateQuantity, totalPrice } = useCart();

  const handleCheckout = () => {
    // TODO: Implement checkout
    console.log('Checkout functionality to be implemented');
  };

  if (items.length === 0) {
    return (
      <div className="p-4 text-center">
        <p className="text-gray-500">Your cart is empty</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Shopping Cart</h2>
      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.product._id} className="flex items-center gap-4 p-4 border rounded-lg">
            <div className="relative w-24 h-24">
              <Image
                src={item.product.image}
                alt={item.product.name}
                fill
                className="object-cover rounded"
              />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">{item.product.name}</h3>
              <p className="text-gray-600">${item.product.price.toFixed(2)}</p>
              <div className="flex items-center gap-2 mt-2">
                <button
                  onClick={() => updateQuantity(item.product._id, item.quantity - 1)}
                  className="px-2 py-1 border rounded hover:bg-gray-100"
                  type="button"
                >
                  -
                </button>
                <span className="w-8 text-center">{item.quantity}</span>
                <button
                  onClick={() => updateQuantity(item.product._id, item.quantity + 1)}
                  className="px-2 py-1 border rounded hover:bg-gray-100"
                  disabled={item.quantity >= item.product.stock}
                  type="button"
                >
                  +
                </button>
              </div>
            </div>
            <div className="text-right">
              <p className="font-semibold">
                ${(item.product.price * item.quantity).toFixed(2)}
              </p>
              <button
                onClick={() => removeItem(item.product._id)}
                className="text-red-500 hover:text-red-700 mt-2"
                type="button"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 border-t pt-4">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold">Total:</span>
          <span className="text-xl font-bold">${totalPrice.toFixed(2)}</span>
        </div>
        <button
          className="w-full mt-4 bg-luxury-gray-700 text-white py-2 px-4 rounded-lg hover:bg-luxury-gray-800 transition-colors"
          onClick={handleCheckout}
          type="button"
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
}; 