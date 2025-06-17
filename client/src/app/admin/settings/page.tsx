'use client';

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface SystemSettings {
  merchant_commission: number;
  buffer_card_limit: number;
  auto_refund_threshold: number;
  notification_email: string;
  maintenance_mode: boolean;
  api_keys: {
    flutterwave: string;
    newegg: string;
    backmarket: string;
  };
}

export default function AdminSettings() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/admin/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSaving(true);

    try {
      const formData = new FormData(e.currentTarget);
      const updatedSettings = {
        merchant_commission: parseFloat(formData.get('merchant_commission') as string),
        buffer_card_limit: parseInt(formData.get('buffer_card_limit') as string),
        auto_refund_threshold: parseFloat(formData.get('auto_refund_threshold') as string),
        notification_email: formData.get('notification_email') as string,
        maintenance_mode: formData.get('maintenance_mode') === 'true',
        api_keys: {
          flutterwave: formData.get('flutterwave_key') as string,
          newegg: formData.get('newegg_key') as string,
          backmarket: formData.get('backmarket_key') as string,
        },
      };

      const response = await fetch('/api/admin/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(updatedSettings),
      });

      if (response.ok) {
        toast.success('Settings updated successfully');
        setSettings(updatedSettings);
      } else {
        throw new Error('Failed to update settings');
      }
    } catch (error) {
      toast.error('Failed to update settings');
    } finally {
      setSaving(false);
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
      <h1 className="text-3xl font-bold mb-8">System Settings</h1>

      <div className="bg-white rounded-lg shadow">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Commission Settings */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Commission Settings</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Merchant Commission Rate (%)
              </label>
              <input
                type="number"
                name="merchant_commission"
                defaultValue={settings?.merchant_commission}
                step="0.01"
                min="0"
                max="100"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                required
              />
            </div>
          </div>

          {/* Buffer Card Settings */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Buffer Card Settings</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Buffer Card Limit
              </label>
              <input
                type="number"
                name="buffer_card_limit"
                defaultValue={settings?.buffer_card_limit}
                min="1"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                required
              />
            </div>
          </div>

          {/* Refund Settings */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Refund Settings</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Auto Refund Threshold ($)
              </label>
              <input
                type="number"
                name="auto_refund_threshold"
                defaultValue={settings?.auto_refund_threshold}
                step="0.01"
                min="0"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                required
              />
            </div>
          </div>

          {/* Notification Settings */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Notification Settings</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Notification Email
              </label>
              <input
                type="email"
                name="notification_email"
                defaultValue={settings?.notification_email}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                required
              />
            </div>
          </div>

          {/* API Keys */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">API Keys</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Flutterwave API Key
              </label>
              <input
                type="password"
                name="flutterwave_key"
                defaultValue={settings?.api_keys.flutterwave}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Newegg API Key
              </label>
              <input
                type="password"
                name="newegg_key"
                defaultValue={settings?.api_keys.newegg}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Back Market API Key
              </label>
              <input
                type="password"
                name="backmarket_key"
                defaultValue={settings?.api_keys.backmarket}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                required
              />
            </div>
          </div>

          {/* System Status */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">System Status</h2>
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="maintenance_mode"
                  defaultChecked={settings?.maintenance_mode}
                  className="rounded border-gray-300 text-luxury-gray-600 shadow-sm focus:border-luxury-gray-500 focus:ring-luxury-gray-500"
                />
                <span className="ml-2 text-sm text-gray-700">Maintenance Mode</span>
              </label>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 bg-luxury-gray-700 text-white rounded-md hover:bg-luxury-gray-800 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 