'use client';

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface Product {
  id: string;
  name: string;
  sku: string;
  price: number;
  stock: number;
  merchant: string;
  category: string;
  status: 'active' | 'inactive';
  last_updated: string;
}

export default function InventoryPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMerchant, setSelectedMerchant] = useState<string>('all');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch('/api/inventory', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      toast.error('Failed to load inventory');
    } finally {
      setLoading(false);
    }
  };

  const handleStockUpdate = async (productId: string, newStock: number) => {
    try {
      const response = await fetch(`/api/inventory/${productId}/stock`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ stock: newStock }),
      });

      if (response.ok) {
        toast.success('Stock updated successfully');
        fetchProducts();
      } else {
        throw new Error('Failed to update stock');
      }
    } catch (error) {
      toast.error('Failed to update stock');
    }
  };

  const handleStatusUpdate = async (productId: string, newStatus: Product['status']) => {
    try {
      const response = await fetch(`/api/inventory/${productId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        toast.success('Product status updated successfully');
        fetchProducts();
      } else {
        throw new Error('Failed to update product status');
      }
    } catch (error) {
      toast.error('Failed to update product status');
    }
  };

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMerchant = selectedMerchant === 'all' || product.merchant === selectedMerchant;
    return matchesSearch && matchesMerchant;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-luxury-gray-700"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Inventory Management</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Products List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Products</h2>
                <div className="flex space-x-4">
                  <input
                    type="text"
                    placeholder="Search products..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                  />
                  <select
                    value={selectedMerchant}
                    onChange={(e) => setSelectedMerchant(e.target.value)}
                    className="rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                  >
                    <option value="all">All Merchants</option>
                    <option value="newegg">Newegg</option>
                    <option value="backmarket">Back Market</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredProducts.map((product) => (
                    <tr 
                      key={product.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedProduct(product)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {product.sku}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {product.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${product.price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <input
                          type="number"
                          value={product.stock}
                          onChange={(e) => handleStockUpdate(product.id, parseInt(e.target.value))}
                          onClick={(e) => e.stopPropagation()}
                          className="w-20 rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          product.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {product.status.charAt(0).toUpperCase() + product.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusUpdate(
                              product.id,
                              product.status === 'active' ? 'inactive' : 'active'
                            );
                          }}
                          className={`${
                            product.status === 'active' ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                          }`}
                        >
                          {product.status === 'active' ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Product Details */}
        <div className="lg:col-span-1">
          {selectedProduct ? (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Product Details</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">SKU</h3>
                  <p className="mt-1">{selectedProduct.sku}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Name</h3>
                  <p className="mt-1">{selectedProduct.name}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Price</h3>
                  <p className="mt-1">${selectedProduct.price.toFixed(2)}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Stock</h3>
                  <p className="mt-1">{selectedProduct.stock} units</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Merchant</h3>
                  <p className="mt-1">{selectedProduct.merchant}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Category</h3>
                  <p className="mt-1">{selectedProduct.category}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Status</h3>
                  <select
                    value={selectedProduct.status}
                    onChange={(e) => handleStatusUpdate(selectedProduct.id, e.target.value as Product['status'])}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Last Updated</h3>
                  <p className="mt-1">{new Date(selectedProduct.last_updated).toLocaleString()}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-500 text-center">Select a product to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 