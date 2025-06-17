'use client';

import React from 'react';
import Navigation from './Navigation';
import { CartProvider } from '@/context/CartContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { MarketplaceProvider } from '@/context/MarketplaceContext';
import { Toaster } from 'react-hot-toast';
import { MarketplaceCSVParser } from '@/components/MarketplaceCSVParser';

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <CartProvider>
        <MarketplaceProvider>
          <Navigation />
          <main className="min-h-screen bg-gray-50">
            {children}
          </main>
          <Toaster position="top-right" />
        </MarketplaceProvider>
      </CartProvider>
    </AuthProvider>
  );
} 