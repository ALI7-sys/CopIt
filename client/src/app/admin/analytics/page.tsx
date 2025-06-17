'use client';

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface SalesData {
  date: string;
  revenue: number;
  orders: number;
  profit: number;
}

interface MerchantPerformance {
  merchant: string;
  total_sales: number;
  total_orders: number;
  profit_margin: number;
  average_order_value: number;
}

export default function AdminAnalytics() {
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [merchantPerformance, setMerchantPerformance] = useState<MerchantPerformance[]>([]);
  const [timeRange, setTimeRange] = useState('7d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      const [salesResponse, merchantResponse] = await Promise.all([
        fetch(`/api/admin/analytics/sales?range=${timeRange}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }),
        fetch('/api/admin/analytics/merchants', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }),
      ]);

      const salesData = await salesResponse.json();
      const merchantData = await merchantResponse.json();

      setSalesData(salesData);
      setMerchantPerformance(merchantData);
    } catch (error) {
      toast.error('Failed to load analytics data');
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
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
        >
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
          <option value="1y">Last Year</option>
        </select>
      </div>

      {/* Sales Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Revenue</h3>
          <p className="text-3xl font-bold">
            ${salesData.reduce((sum, day) => sum + day.revenue, 0).toFixed(2)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Over selected period</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Orders</h3>
          <p className="text-3xl font-bold">
            {salesData.reduce((sum, day) => sum + day.orders, 0)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Over selected period</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Profit</h3>
          <p className="text-3xl font-bold">
            ${salesData.reduce((sum, day) => sum + day.profit, 0).toFixed(2)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Over selected period</p>
        </div>
      </div>

      {/* Merchant Performance */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Merchant Performance</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Merchant</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Sales</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Orders</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Profit Margin</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg. Order Value</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {merchantPerformance.map((merchant) => (
                <tr key={merchant.merchant}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {merchant.merchant}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${merchant.total_sales.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {merchant.total_orders}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {merchant.profit_margin}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${merchant.average_order_value.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Daily Sales Chart */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Daily Sales</h2>
        </div>
        <div className="p-6">
          <div className="h-64">
            {/* Chart will be implemented here */}
            <p className="text-gray-500 text-center">Sales chart visualization will be added here</p>
          </div>
        </div>
      </div>
    </div>
  );
} 