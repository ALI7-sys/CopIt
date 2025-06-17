import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ message: 'Checkout summary endpoint' });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    return NextResponse.json({ message: 'Checkout summary processed', data: body });
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request body' },
      { status: 400 }
    );
  }
} 