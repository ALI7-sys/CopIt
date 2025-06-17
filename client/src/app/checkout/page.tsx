'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCart } from '@/context/CartContext';
import { PaymentService } from '@/services/payment';
import { toast } from 'react-hot-toast';

interface ErrorResponse {
  status: 'failed';
  error: string;
  error_type: 'payment_error' | 'api_version_error' | 'card_not_found' | 'checkout_error' | 'server_error';
}

export default function CheckoutPage() {
  const router = useRouter();
  const { items, totalPrice, clearCart } = useCart();
  const [loading, setLoading] = useState(false);
  const [paymentService] = useState(() => PaymentService.getInstance());
  const [selectedMerchant, setSelectedMerchant] = useState<string>('');
  const [usingBufferCard, setUsingBufferCard] = useState(false);

  const handleCheckout = async () => {
    if (!items.length) {
      toast.error('Your cart is empty');
      return;
    }

    if (!selectedMerchant) {
      toast.error('Please select a merchant');
      return;
    }

    setLoading(true);
    try {
      // Step 1: Create or get virtual card
      const cardResponse = await paymentService.createVirtualCard(
        totalPrice,
        selectedMerchant
      );

      if (cardResponse.status === 'failed') {
        throw new Error(cardResponse.error);
      }

      // Check if we're using a buffer card
      setUsingBufferCard(cardResponse.data.is_buffer === true);

      // Step 2: Initialize payment
      const paymentResponse = await paymentService.initializePayment(
        totalPrice,
        'USD'
      );

      if (paymentResponse.status === 'failed') {
        throw new Error(paymentResponse.error);
      }

      // Step 3: Process the order
      const orderResponse = await fetch('/api/checkout/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items,
          payment_card_id: cardResponse.data.card_id,
          merchant: selectedMerchant,
          is_buffer: cardResponse.data.is_buffer
        }),
      });

      const orderResult = await orderResponse.json();

      if (orderResult.status === 'success') {
        if (usingBufferCard) {
          toast.success('Order placed successfully with instant checkout!');
        } else {
          toast.success('Order placed successfully! Your virtual card will be ready in 1-2 hours.');
        }
        clearCart();
        router.push('/order-confirmation');
      } else {
        const errorResponse = orderResult as ErrorResponse;
        let errorMessage = errorResponse.error;

        // Handle specific error types
        switch (errorResponse.error_type) {
          case 'payment_error':
            errorMessage = 'Payment processing failed. Please try again.';
            break;
          case 'api_version_error':
            errorMessage = 'System error. Please try again later.';
            break;
          case 'card_not_found':
            errorMessage = 'Payment card not found. Please check your card details.';
            break;
          case 'checkout_error':
            errorMessage = 'Checkout processing failed. Please try again.';
            break;
          case 'server_error':
            errorMessage = 'Server error. Please try again later.';
            break;
        }

        toast.error(errorMessage);
      }
    } catch (error) {
      toast.error('Failed to process order. Please try again later.');
      console.error('Error processing order:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="border rounded-lg p-6 bg-white">
            <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
            <div className="space-y-4">
              {items.map((item) => (
                <div key={item.product._id} className="flex justify-between">
                  <span>{item.product.name} x {item.quantity}</span>
                  <span>${(item.product.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
              <div className="border-t pt-4">
                <div className="flex justify-between font-bold">
                  <span>Total</span>
                  <span>${totalPrice.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="border rounded-lg p-6 bg-white">
            <h2 className="text-xl font-semibold mb-4">Select Merchant</h2>
            <div className="space-y-4">
              <select
                value={selectedMerchant}
                onChange={(e) => setSelectedMerchant(e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="">Select a merchant</option>
                <option value="newegg">Newegg</option>
                <option value="backmarket">Back Market</option>
              </select>
            </div>
          </div>
        </div>

        <div className="border rounded-lg p-6 bg-white">
          <h2 className="text-xl font-semibold mb-4">Payment Information</h2>
          <p className="text-gray-600 mb-4">
            {usingBufferCard ? (
              <span className="text-green-600 font-medium">
                ✓ Instant checkout available! Your order will be processed immediately.
              </span>
            ) : (
              <>
                Your payment will be processed securely using a virtual card.
                The card will be automatically generated and linked to your selected merchant.
                <br /><br />
                <span className="text-yellow-600">
                  Note: Virtual card creation may take 1-2 hours. You'll be notified when it's ready.
                </span>
              </>
            )}
          </p>
          <button
            onClick={handleCheckout}
            disabled={loading || !selectedMerchant}
            className={`w-full py-3 px-4 rounded-lg text-white font-semibold ${
              loading || !selectedMerchant
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-luxury-gray-700 hover:bg-luxury-gray-800'
            }`}
          >
            {loading ? 'Processing...' : 'Complete Purchase'}
          </button>
        </div>
      </div>
    </div>
  );
} 