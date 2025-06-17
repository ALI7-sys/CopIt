import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { items, shipping_address, payment_card_id } = await request.json();

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/checkout/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        items,
        shipping_address,
        payment_card_id
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to process order' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error processing order:', error);
    return NextResponse.json(
      { error: 'Failed to process order' },
      { status: 500 }
    );
  }
} 