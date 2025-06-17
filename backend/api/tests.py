from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Product
from decimal import Decimal

User = get_user_model()

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('99.99'),
            stock=10,
            image_url='https://example.com/image.jpg',
            source_url='https://example.com/product'
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.stock, 10)

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            name='Test User'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.name, 'Test User')
        self.assertTrue(self.user.check_password('testpass123'))

class ProductAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            name='Test User'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('99.99'),
            stock=10,
            image_url='https://example.com/image.jpg',
            source_url='https://example.com/product'
        )
        
        # Get token
        response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_product(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_create_product(self):
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '149.99',
            'stock': 5,
            'image_url': 'https://example.com/new.jpg',
            'source_url': 'https://example.com/new'
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

    def test_user_registration(self):
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_user_login(self):
        # Create user first
        User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['email'].split('@')[0],
            password=self.user_data['password'],
            name=self.user_data['name']
        )
        
        response = self.client.post('/api/auth/login/', {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_profile(self):
        # Create and login user
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['email'].split('@')[0],
            password=self.user_data['password'],
            name=self.user_data['name']
        )
        
        response = self.client.post('/api/auth/login/', {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        token = response.data['access']
        
        # Test profile endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email']) 