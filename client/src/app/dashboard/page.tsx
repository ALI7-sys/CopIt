'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';

interface BusinessProfile {
  company_name: string;
  tax_id: string;
  business_address: string;
  verification_status: 'pending' | 'verified' | 'rejected';
}

interface SalesMetrics {
  total_sales: number;
  total_orders: number;
  average_order_value: number;
  profit_margin: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [businessProfile, setBusinessProfile] = useState<BusinessProfile | null>(null);
  const [salesMetrics, setSalesMetrics] = useState<SalesMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBusinessProfile();
    fetchSalesMetrics();
  }, []);

  const fetchBusinessProfile = async () => {
    try {
      const response = await fetch('/api/business/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setBusinessProfile(data);
    } catch (error) {
      toast.error('Failed to load business profile');
    }
  };

  const fetchSalesMetrics = async () => {
    try {
      const response = await fetch('/api/analytics/sales', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setSalesMetrics(data);
    } catch (error) {
      toast.error('Failed to load sales metrics');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    try {
      const response = await fetch('/api/business/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          company_name: formData.get('company_name'),
          tax_id: formData.get('tax_id'),
          business_address: formData.get('business_address'),
        }),
      });

      if (response.ok) {
        toast.success('Business profile updated successfully');
        fetchBusinessProfile();
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (error) {
      toast.error('Failed to update business profile');
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
      <h1 className="text-3xl font-bold mb-8">Merchant Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Business Profile Section */}
        <div className="space-y-6">
          <div className="border rounded-lg p-6 bg-white">
            <h2 className="text-xl font-semibold mb-4">Business Profile</h2>
            {businessProfile ? (
              <form onSubmit={handleProfileUpdate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Company Name</label>
                  <input
                    type="text"
                    name="company_name"
                    defaultValue={businessProfile.company_name}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tax ID / EIN</label>
                  <input
                    type="text"
                    name="tax_id"
                    defaultValue={businessProfile.tax_id}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Business Address</label>
                  <textarea
                    name="business_address"
                    defaultValue={businessProfile.business_address}
                    rows={3}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                    required
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">
                    Verification Status: 
                    <span className={`ml-2 font-medium ${
                      businessProfile.verification_status === 'verified' ? 'text-green-600' :
                      businessProfile.verification_status === 'rejected' ? 'text-red-600' :
                      'text-yellow-600'
                    }`}>
                      {businessProfile.verification_status.charAt(0).toUpperCase() + 
                       businessProfile.verification_status.slice(1)}
                    </span>
                  </span>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-luxury-gray-700 text-white rounded-md hover:bg-luxury-gray-800"
                  >
                    Update Profile
                  </button>
                </div>
              </form>
            ) : (
              <p className="text-gray-500">No business profile found. Please complete your profile.</p>
            )}
          </div>
        </div>

        {/* Sales Metrics Section */}
        <div className="space-y-6">
          <div className="border rounded-lg p-6 bg-white">
            <h2 className="text-xl font-semibold mb-4">Sales Overview</h2>
            {salesMetrics ? (
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Total Sales</h3>
                  <p className="text-2xl font-bold">${salesMetrics.total_sales.toFixed(2)}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Total Orders</h3>
                  <p className="text-2xl font-bold">{salesMetrics.total_orders}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Average Order Value</h3>
                  <p className="text-2xl font-bold">${salesMetrics.average_order_value.toFixed(2)}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Profit Margin</h3>
                  <p className="text-2xl font-bold">{salesMetrics.profit_margin}%</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No sales data available yet.</p>
            )}
          </div>

          <div className="border rounded-lg p-6 bg-white">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-4">
              <button
                onClick={() => router.push('/orders')}
                className="w-full px-4 py-2 bg-luxury-gray-700 text-white rounded-md hover:bg-luxury-gray-800"
              >
                View Orders
              </button>
              <button
                onClick={() => router.push('/inventory')}
                className="w-full px-4 py-2 bg-luxury-gray-700 text-white rounded-md hover:bg-luxury-gray-800"
              >
                Manage Inventory
              </button>
              <button
                onClick={() => router.push('/analytics')}
                className="w-full px-4 py-2 bg-luxury-gray-700 text-white rounded-md hover:bg-luxury-gray-800"
              >
                View Analytics
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 