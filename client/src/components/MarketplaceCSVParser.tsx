'use client';

import React, { useState, useCallback } from 'react';
import { parseMarketplaceCSV } from '@/utils/marketplaceParser';
import { ParseResult } from '@/types/marketplace';
import { Button, Box, Typography, Alert, CircularProgress } from '@mui/material';

interface MarketplaceCSVParserProps {
  onProductsParsed: (result: ParseResult) => void;
}

export const MarketplaceCSVParser: React.FC<MarketplaceCSVParserProps> = ({ onProductsParsed }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMarketplace, setSelectedMarketplace] = useState<'backmarket' | 'newegg'>('backmarket');

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await parseMarketplaceCSV(file, selectedMarketplace);
      onProductsParsed(result);

      if (result.errors.length > 0) {
        setError(`Found ${result.errors.length} errors during parsing. Check console for details.`);
        console.error('Parsing errors:', result.errors);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse CSV file');
    } finally {
      setIsLoading(false);
    }
  }, [selectedMarketplace, onProductsParsed]);

  return (
    <Box sx={{ p: 3, border: '1px dashed #ccc', borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Import Products from CSV
      </Typography>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Select Marketplace:
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant={selectedMarketplace === 'backmarket' ? 'contained' : 'outlined'}
            onClick={() => setSelectedMarketplace('backmarket')}
          >
            Backmarket
          </Button>
          <Button
            variant={selectedMarketplace === 'newegg' ? 'contained' : 'outlined'}
            onClick={() => setSelectedMarketplace('newegg')}
          >
            Newegg
          </Button>
        </Box>
      </Box>

      <Box sx={{ mb: 2 }}>
        <input
          accept=".csv"
          style={{ display: 'none' }}
          id="csv-file-upload"
          type="file"
          onChange={handleFileUpload}
          disabled={isLoading}
        />
        <label htmlFor="csv-file-upload">
          <Button
            variant="contained"
            component="span"
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
          >
            {isLoading ? 'Processing...' : 'Upload CSV File'}
          </Button>
        </label>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        Supported file format: CSV
        <br />
        {selectedMarketplace === 'backmarket' ? (
          <>
            Required fields: id, name, price, description, image, category, stock, condition, seller, url,
            warranty, refurbishedGrade, originalPrice, discount
          </>
        ) : (
          <>
            Required fields: id, name, price, description, image, category, stock, condition, seller, url,
            brand, model, sku, shippingPrice, shippingMethod, shippingDays
          </>
        )}
      </Typography>
    </Box>
  );
}; 