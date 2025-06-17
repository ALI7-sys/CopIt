import React from 'react';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navigation from '@/components/Navigation';
import { CartProvider } from '@/context/CartContext';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CopIt - Product Management',
  description: 'Manage your products with ease',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CartProvider>
          <Navigation />
          <main className="min-h-screen bg-gray-50">
            {children}
          </main>
          <Toaster position="top-right" />
        </CartProvider>
      </body>
    </html>
  );
} 