import axios from 'axios';

const API_URL = 'http://localhost:8001/api';

interface TokenResponse {
  access: string;
  refresh: string;
}

interface AuthResponse {
  data: {
    user: {
      id: number;
      email: string;
      name: string;
    };
    tokens: TokenResponse;
  };
  message: string;
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/login/', { email, password });
    return response.data;
  },
  register: async (email: string, password: string, name: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/signup/', { email, password, name });
    return response.data;
  },
  getCurrentUser: async (): Promise<AuthResponse> => {
    const response = await api.get<AuthResponse>('/profile/');
    return response.data;
  },
};

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  stock: number;
  created_at: string;
  updated_at: string;
}

// Products API
export const productsAPI = {
  getAll: async (): Promise<Product[]> => {
    const response = await api.get<Product[]>('/products/');
    return response.data;
  },
  getById: async (id: number): Promise<Product> => {
    const response = await api.get<Product>(`/products/${id}/`);
    return response.data;
  },
  create: async (data: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<Product> => {
    const response = await api.post<Product>('/products/', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Product>): Promise<Product> => {
    const response = await api.put<Product>(`/products/${id}/`, data);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}/`);
  },
};

export default api; 