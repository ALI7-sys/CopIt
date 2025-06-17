import { toast as hotToast } from 'react-hot-toast';

export const toast = {
  success: (message: string) =>
    hotToast.success(message, {
      duration: 4000,
      style: {
        background: '#10B981',
        color: '#fff',
        padding: '16px',
        borderRadius: '8px',
      },
      iconTheme: {
        primary: '#fff',
        secondary: '#10B981',
      },
    }),

  error: (message: string) =>
    hotToast.error(message, {
      duration: 4000,
      style: {
        background: '#EF4444',
        color: '#fff',
        padding: '16px',
        borderRadius: '8px',
      },
      iconTheme: {
        primary: '#fff',
        secondary: '#EF4444',
      },
    }),

  loading: (message: string) =>
    hotToast.loading(message, {
      duration: 4000,
      style: {
        background: '#3B82F6',
        color: '#fff',
        padding: '16px',
        borderRadius: '8px',
      },
    }),
}; 