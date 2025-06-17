export const API_CONFIG = {
  REVOLUT_API_KEY: process.env.NEXT_PUBLIC_REVOLUT_API_KEY || '',
  SUPPORTED_MERCHANTS: {
    newegg: {
      merchant_id: process.env.NEXT_PUBLIC_NEWEGG_MERCHANT_ID || '',
      name: 'Newegg',
      logo: '/images/merchants/newegg.png'
    },
    backmarket: {
      merchant_id: process.env.NEXT_PUBLIC_BACKMARKET_MERCHANT_ID || '',
      name: 'Back Market',
      logo: '/images/merchants/backmarket.png'
    }
  }
} as const; 