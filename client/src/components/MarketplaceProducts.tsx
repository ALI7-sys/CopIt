'use client';

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { useMarketplace } from '@/context/MarketplaceContext';
import { MarketplaceProduct } from '@/types/marketplace';
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
  Slider,
  Button,
  Switch,
  FormControlLabel,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import SaveIcon from '@mui/icons-material/Save';

type SortField = 'name' | 'price' | 'stock';
type SortOrder = 'asc' | 'desc';
type MarketplaceFilter = 'all' | 'backmarket' | 'newegg';
type StockStatus = 'all' | 'inStock' | 'outOfStock';

interface FilterPreferences {
  searchTerm: string;
  sortField: SortField;
  sortOrder: SortOrder;
  marketplaceFilter: MarketplaceFilter;
  priceRange: [number, number];
  stockStatus: StockStatus;
  showOnlyDiscounted: boolean;
}

const DEFAULT_FILTERS: FilterPreferences = {
  searchTerm: '',
  sortField: 'name',
  sortOrder: 'asc',
  marketplaceFilter: 'all',
  priceRange: [0, 1000],
  stockStatus: 'all',
  showOnlyDiscounted: false,
};

export const MarketplaceProducts: React.FC = () => {
  const { products, removeProduct, stats } = useMarketplace();
  const [filters, setFilters] = useState<FilterPreferences>(() => {
    const saved = localStorage.getItem('marketplaceFilters');
    return saved ? JSON.parse(saved) : DEFAULT_FILTERS;
  });

  // Save filters to localStorage when they change
  useEffect(() => {
    localStorage.setItem('marketplaceFilters', JSON.stringify(filters));
  }, [filters]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'f':
            e.preventDefault();
            document.getElementById('search-field')?.focus();
            break;
          case 'r':
            e.preventDefault();
            resetFilters();
            break;
          case 's':
            e.preventDefault();
            saveFilters();
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  const updateFilter = useCallback((key: keyof FilterPreferences, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const saveFilters = useCallback(() => {
    localStorage.setItem('marketplaceFilters', JSON.stringify(filters));
  }, [filters]);

  // Filter and sort products
  const filteredAndSortedProducts = useMemo(() => {
    return products
      .filter(product => {
        const matchesSearch = 
          product.name.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
          product.description.toLowerCase().includes(filters.searchTerm.toLowerCase());
        
        const matchesMarketplace = 
          filters.marketplaceFilter === 'all' || 
          product.marketplace === filters.marketplaceFilter;

        const matchesPriceRange = 
          product.price >= filters.priceRange[0] && 
          product.price <= filters.priceRange[1];

        const matchesStockStatus = 
          filters.stockStatus === 'all' ||
          (filters.stockStatus === 'inStock' && product.stock > 0) ||
          (filters.stockStatus === 'outOfStock' && product.stock === 0);

        const matchesDiscount = 
          !filters.showOnlyDiscounted || 
          (product.marketplace === 'backmarket' && product.discount > 0);

        return matchesSearch && matchesMarketplace && matchesPriceRange && 
               matchesStockStatus && matchesDiscount;
      })
      .sort((a, b) => {
        let comparison = 0;
        switch (filters.sortField) {
          case 'name':
            comparison = a.name.localeCompare(b.name);
            break;
          case 'price':
            comparison = a.price - b.price;
            break;
          case 'stock':
            comparison = a.stock - b.stock;
            break;
        }
        return filters.sortOrder === 'asc' ? comparison : -comparison;
      });
  }, [products, filters]);

  if (products.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No products imported yet
        </Typography>
      </Box>
    );
  }

  // Calculate price range for slider
  const priceRange = useMemo(() => {
    const prices = products.map(p => p.price);
    return [Math.min(...prices), Math.max(...prices)];
  }, [products]);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Chip label={`Total: ${stats.total}`} color="primary" />
        <Chip label={`Backmarket: ${stats.backmarket}`} color="secondary" />
        <Chip label={`Newegg: ${stats.newegg}`} color="info" />
      </Box>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
        <TextField
          id="search-field"
          label="Search Products"
          variant="outlined"
          size="small"
          value={filters.searchTerm}
          onChange={(e) => updateFilter('searchTerm', e.target.value)}
          sx={{ flex: 1 }}
          InputProps={{
            endAdornment: (
              <Typography variant="caption" color="text.secondary">
                Ctrl+F
              </Typography>
            ),
          }}
        />

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Marketplace</InputLabel>
          <Select
            value={filters.marketplaceFilter}
            label="Marketplace"
            onChange={(e) => updateFilter('marketplaceFilter', e.target.value)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="backmarket">Backmarket</MenuItem>
            <MenuItem value="newegg">Newegg</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={filters.sortField}
            label="Sort By"
            onChange={(e) => updateFilter('sortField', e.target.value)}
          >
            <MenuItem value="name">Name</MenuItem>
            <MenuItem value="price">Price</MenuItem>
            <MenuItem value="stock">Stock</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Order</InputLabel>
          <Select
            value={filters.sortOrder}
            label="Order"
            onChange={(e) => updateFilter('sortOrder', e.target.value)}
          >
            <MenuItem value="asc">Ascending</MenuItem>
            <MenuItem value="desc">Descending</MenuItem>
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          startIcon={<RestartAltIcon />}
          onClick={resetFilters}
          size="small"
          title="Reset Filters (Ctrl+R)"
        >
          Reset
        </Button>

        <Button
          variant="outlined"
          startIcon={<SaveIcon />}
          onClick={saveFilters}
          size="small"
          title="Save Filters (Ctrl+S)"
        >
          Save
        </Button>
      </Stack>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Typography gutterBottom>Price Range</Typography>
          <Slider
            value={filters.priceRange}
            onChange={(_, value) => updateFilter('priceRange', value)}
            valueLabelDisplay="auto"
            min={priceRange[0]}
            max={priceRange[1]}
            valueLabelFormat={(value) => `$${value}`}
          />
        </Box>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Stock Status</InputLabel>
          <Select
            value={filters.stockStatus}
            label="Stock Status"
            onChange={(e) => updateFilter('stockStatus', e.target.value)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="inStock">In Stock</MenuItem>
            <MenuItem value="outOfStock">Out of Stock</MenuItem>
          </Select>
        </FormControl>

        <FormControlLabel
          control={
            <Switch
              checked={filters.showOnlyDiscounted}
              onChange={(e) => updateFilter('showOnlyDiscounted', e.target.checked)}
            />
          }
          label="Show Only Discounted"
        />
      </Stack>

      <Grid container spacing={3}>
        {filteredAndSortedProducts.map((product) => (
          <Grid item xs={12} sm={6} md={4} key={product.id}>
            <ProductCard product={product} onDelete={removeProduct} />
          </Grid>
        ))}
      </Grid>

      {filteredAndSortedProducts.length === 0 && (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No products match your filters
          </Typography>
        </Box>
      )}
    </Box>
  );
};

interface ProductCardProps {
  product: MarketplaceProduct;
  onDelete: (id: string) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onDelete }) => {
  const isBackmarket = product.marketplace === 'backmarket';

  return (
    <Card>
      <CardMedia
        component="img"
        height="200"
        image={product.image}
        alt={product.name}
        sx={{ objectFit: 'contain', bgcolor: 'grey.100' }}
      />
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Typography variant="h6" component="div" sx={{ flex: 1 }}>
            {product.name}
          </Typography>
          <Box>
            <Tooltip title="Edit">
              <IconButton size="small" sx={{ mr: 1 }}>
                <EditIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton size="small" onClick={() => onDelete(product.id)}>
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {product.description}
        </Typography>

        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label={product.marketplace}
            color={isBackmarket ? 'secondary' : 'info'}
            size="small"
          />
          <Chip
            label={`$${product.price.toFixed(2)}`}
            color="primary"
            size="small"
          />
          <Chip
            label={`Stock: ${product.stock}`}
            color={product.stock > 0 ? 'success' : 'error'}
            size="small"
          />
          {isBackmarket && (
            <>
              <Chip
                label={product.refurbishedGrade}
                color="warning"
                size="small"
              />
              <Chip
                label={`${product.discount}% off`}
                color="error"
                size="small"
              />
            </>
          )}
        </Box>

        {!isBackmarket && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Brand: {product.brand}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Model: {product.model}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Shipping: ${product.shipping.price} ({product.shipping.method})
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}; 