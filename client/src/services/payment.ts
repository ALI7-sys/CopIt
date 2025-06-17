import { toast } from 'react-hot-toast';

interface PaymentResponse {
  status: 'success' | 'failed';
  data?: any;
  error?: string;
  error_type?: 'payment_error' | 'api_version_error' | 'card_not_found' | 'checkout_error' | 'server_error';
}

export class PaymentService {
  private static instance: PaymentService;
  private baseUrl: string;
  private bufferCards: Map<string, { cardId: string; amount: number; merchant: string; timestamp: number }>;

  private constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.bufferCards = new Map();
    this.loadBufferCards();
  }

  private loadBufferCards() {
    const savedCards = localStorage.getItem('buffer_cards');
    if (savedCards) {
      this.bufferCards = new Map(JSON.parse(savedCards));
    }
  }

  private saveBufferCards() {
    localStorage.setItem('buffer_cards', JSON.stringify(Array.from(this.bufferCards.entries())));
  }

  public static getInstance(): PaymentService {
    if (!PaymentService.instance) {
      PaymentService.instance = new PaymentService();
    }
    return PaymentService.instance;
  }

  async getBufferCard(merchant: string, amount: number): Promise<PaymentResponse> {
    const now = Date.now();
    const bufferKey = `${merchant}_${amount}`;
    
    // Check if we have a valid buffer card
    if (this.bufferCards.has(bufferKey)) {
      const bufferCard = this.bufferCards.get(bufferKey)!;
      // Check if card is still valid (less than 1 hour old)
      if (now - bufferCard.timestamp < 3600000) {
        return {
          status: 'success',
          data: { card_id: bufferCard.cardId }
        };
      }
      // Remove expired buffer card
      this.bufferCards.delete(bufferKey);
      this.saveBufferCards();
    }

    // Create new buffer card
    try {
      const response = await fetch(`${this.baseUrl}/api/cards/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          amount,
          merchant,
          is_buffer: true
        }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Store buffer card
        this.bufferCards.set(bufferKey, {
          cardId: data.data.card_id,
          amount,
          merchant,
          timestamp: now
        });
        this.saveBufferCards();
      }
      
      return data;
    } catch (error) {
      console.error('Buffer card creation failed:', error);
      return {
        status: 'failed',
        error: 'Failed to create buffer card',
        error_type: 'payment_error',
      };
    }
  }

  async initializePayment(amount: number, currency: string = 'USD'): Promise<PaymentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/payments/initialize/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          amount,
          currency,
          payment_type: 'card',
        }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Payment initialization failed:', error);
      return {
        status: 'failed',
        error: 'Failed to initialize payment',
        error_type: 'payment_error',
      };
    }
  }

  async verifyPayment(transactionId: string): Promise<PaymentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/payments/verify/${transactionId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Payment verification failed:', error);
      return {
        status: 'failed',
        error: 'Failed to verify payment',
        error_type: 'payment_error',
      };
    }
  }

  async createVirtualCard(amount: number, merchant: string): Promise<PaymentResponse> {
    // First try to get a buffer card
    const bufferResponse = await this.getBufferCard(merchant, amount);
    if (bufferResponse.status === 'success') {
      return bufferResponse;
    }

    // If no buffer card available, create a new one
    try {
      const response = await fetch(`${this.baseUrl}/api/cards/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          amount,
          merchant,
          is_buffer: false
        }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Virtual card creation failed:', error);
      return {
        status: 'failed',
        error: 'Failed to create virtual card',
        error_type: 'payment_error',
      };
    }
  }

  async getCardDetails(cardId: string): Promise<PaymentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/cards/${cardId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get card details:', error);
      return {
        status: 'failed',
        error: 'Failed to get card details',
        error_type: 'card_not_found',
      };
    }
  }

  async listActiveCards(): Promise<PaymentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/cards/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to list cards:', error);
      return {
        status: 'failed',
        error: 'Failed to list cards',
        error_type: 'server_error',
      };
    }
  }

  async cancelCard(cardId: string): Promise<PaymentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/cards/${cardId}/cancel/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to cancel card:', error);
      return {
        status: 'failed',
        error: 'Failed to cancel card',
        error_type: 'card_not_found',
      };
    }
  }
} 