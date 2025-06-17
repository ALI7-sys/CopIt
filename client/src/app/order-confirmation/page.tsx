'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface OrderDetails {
  order: {
    items: Array<{
      product: {
        _id: string;
        name: string;
        price: number;
        image: string;
      };
      quantity: number;
    }>;
    totals: {
      subtotal: number;
      fulfillment_commission: number;
      shipping_fee: number;
      total: number;
    };
    shipping_address: {
      street: string;
      city: string;
      state: string;
      zip: string;
      country: string;
    };
    payment: {
      card_id: string;
      transaction_id: string;
      status: string;
    };
  };
}

export default function OrderConfirmationPage() {
  const router = useRouter();
  const [orderDetails, setOrderDetails] = useState<OrderDetails | null>(null);

  useEffect(() => {
    // In a real application, you would fetch the order details from your backend
    // For now, we'll just redirect to home if there's no order
    if (!orderDetails) {
      router.push('/');
    }
  }, [orderDetails, router]);

  if (!orderDetails) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-luxury-gray-900 mb-2">Order Confirmed!</h1>
          <p className="text-luxury-gray-600">Thank you for your purchase</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-luxury-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-luxury-gray-900">Order Details</h2>
          
          {/* Order Items */}
          <div className="space-y-4 mb-6">
            {orderDetails.order.items.map((item) => (
              <div key={item.product._id} className="flex items-center gap-4">
                <div className="w-20 h-20 relative">
                  <img
                    src={item.product.image}
                    alt={item.product.name}
                    className="object-cover rounded"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{item.product.name}</h3>
                  <p className="text-luxury-gray-600">Quantity: {item.quantity}</p>
                  <p className="font-medium">${(item.product.price * item.quantity).toFixed(2)}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div className="border-t border-luxury-gray-200 pt-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-luxury-gray-600">Subtotal</span>
                <span className="font-medium">${orderDetails.order.totals.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-luxury-gray-600">Fulfillment Commission (2%)</span>
                <span className="font-medium">${orderDetails.order.totals.fulfillment_commission.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-luxury-gray-600">Shipping</span>
                <span className="font-medium">
                  {orderDetails.order.totals.shipping_fee === 0 ? 'Free' : `$${orderDetails.order.totals.shipping_fee.toFixed(2)}`}
                </span>
              </div>
              <div className="border-t border-luxury-gray-200 pt-2 mt-2">
                <div className="flex justify-between">
                  <span className="font-semibold">Total</span>
                  <span className="font-bold text-lg">${orderDetails.order.totals.total.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Shipping Information */}
        <div className="bg-white rounded-lg shadow-sm border border-luxury-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-luxury-gray-900">Shipping Information</h2>
          <div className="space-y-2">
            <p>{orderDetails.order.shipping_address.street}</p>
            <p>
              {orderDetails.order.shipping_address.city}, {orderDetails.order.shipping_address.state} {orderDetails.order.shipping_address.zip}
            </p>
            <p>{orderDetails.order.shipping_address.country}</p>
          </div>
        </div>

        {/* Payment Information */}
        <div className="bg-white rounded-lg shadow-sm border border-luxury-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-luxury-gray-900">Payment Information</h2>
          <div className="space-y-2">
            <p>Transaction ID: {orderDetails.order.payment.transaction_id}</p>
            <p>Status: <span className="text-green-600 font-medium">{orderDetails.order.payment.status}</span></p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-4">
          <Link
            href="/"
            className="px-6 py-2 border border-luxury-gray-300 rounded-md text-luxury-gray-700 hover:bg-luxury-gray-50"
          >
            Continue Shopping
          </Link>
          <button
            onClick={() => window.print()}
            className="px-6 py-2 bg-luxury-gray-700 text-white rounded-md hover:bg-luxury-gray-800"
          >
            Print Receipt
          </button>
        </div>
      </div>
    </div>
  );
} 