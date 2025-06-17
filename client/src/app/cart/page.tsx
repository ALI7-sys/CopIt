'use client';

import React from 'react';
import { Cart } from '@/components/Cart';

export default function CartPage(): React.JSX.Element {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Shopping Cart</h1>
      <Cart />
    </main>
  );
} 