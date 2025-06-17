'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';

interface DashboardStats {
  total_orders: number;
  total_revenue: number;
  active_products: number;
  pending_orders: number;
  profit_margin: number;
  average_order_value: number;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('/api/admin/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      toast.error('Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-luxury-gray-700"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Orders</h3>
          <p className="text-3xl font-bold">{stats?.total_orders || 0}</p>
          <p className="text-sm text-gray-500 mt-2">
            {stats?.pending_orders || 0} pending orders
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Revenue</h3>
          <p className="text-3xl font-bold">${stats?.total_revenue?.toFixed(2) || '0.00'}</p>
          <p className="text-sm text-gray-500 mt-2">
            Avg. Order: ${stats?.average_order_value?.toFixed(2) || '0.00'}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Active Products</h3>
          <p className="text-3xl font-bold">{stats?.active_products || 0}</p>
          <p className="text-sm text-gray-500 mt-2">
            Profit Margin: {stats?.profit_margin || 0}%
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <button
          onClick={() => router.push('/admin/orders')}
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Order Management</h3>
          <p className="text-sm text-gray-500">View and manage all orders</p>
        </button>
        <button
          onClick={() => router.push('/admin/inventory')}
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Inventory</h3>
          <p className="text-sm text-gray-500">Manage product inventory</p>
        </button>
        <button
          onClick={() => router.push('/admin/analytics')}
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Analytics</h3>
          <p className="text-sm text-gray-500">View detailed sales analytics</p>
        </button>
        <button
          onClick={() => router.push('/admin/settings')}
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Settings</h3>
          <p className="text-sm text-gray-500">Configure system settings</p>
        </button>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Recent Activity</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {/* Activity items will be populated here */}
            <p className="text-gray-500 text-center">No recent activity</p>
          </div>
        </div>
      </div>
    </div>
  );
} 