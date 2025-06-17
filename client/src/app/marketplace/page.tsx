'use client';

import { useState, useEffect } from 'react';
import { API_CONFIG } from '@/config/api';
import { Product } from '@/types/product';
import ProductCard from '@/components/ProductCard';
import { useCart } from '@/context/CartContext';

export default function MarketplacePage(): React.JSX.Element {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { addItem } = useCart();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('/api/products');
        if (!response.ok) {
          throw new Error('Failed to fetch products');
        }
        const data = await response.json();
        const typedProducts: Product[] = data.map((product: any) => ({
          _id: product._id,
          name: product.name,
          description: product.description,
          price: product.price,
          image: product.image,
          stock: product.stock,
          category: product.category,
          brand: product.brand,
          createdAt: product.createdAt,
          updatedAt: product.updatedAt
        }));
        setProducts(typedProducts);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center min-h-screen text-red-500">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Marketplace</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <ProductCard
            key={product._id}
            product={product}
            onAddToCart={() => addItem(product)}
          />
        ))}
      </div>
    </div>
  );
} 