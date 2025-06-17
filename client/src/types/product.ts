export interface Product {
  _id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  stock: number;
  category: string;
  brand: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProductResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
} 