'use client';

import React from 'react';
import QRCodeGenerator from '@/components/QRCodeGenerator';

export default function QRCodePage(): React.JSX.Element {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">QR Code Generator</h1>
      <QRCodeGenerator />
    </main>
  );
} 