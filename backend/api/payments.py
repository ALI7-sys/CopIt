import requests
from django.conf import settings
from rest_framework.exceptions import APIException
import time

class FlutterwavePaymentError(APIException):
    status_code = 400
    default_detail = 'Payment processing failed'
    default_code = 'payment_error'

class FlutterwavePayment:
    def __init__(self):
        self.public_key = settings.FLUTTERWAVE_PUBLIC_KEY
        self.secret_key = settings.FLUTTERWAVE_SECRET_KEY
        self.encryption_key = settings.FLUTTERWAVE_ENCRYPTION_KEY
        self.api_url = 'https://api.flutterwave.com/v3'
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initialize_payment(self, user, amount, currency='USD', payment_type='card'):
        """Initialize a payment transaction"""
        try:
            response = requests.post(
                f'{self.api_url}/payments',
                headers=self.headers,
                json={
                    'tx_ref': f"tx_{user.id}_{int(time.time())}",
                    'amount': amount,
                    'currency': currency,
                    'payment_type': payment_type,
                    'customer': {
                        'email': user.email,
                        'name': user.get_full_name() or user.username
                    },
                    'customizations': {
                        'title': 'E-commerce Payment',
                        'description': 'Payment for your order'
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FlutterwavePaymentError(f'Failed to initialize payment: {str(e)}')
    
    def verify_payment(self, transaction_id):
        """Verify a payment transaction"""
        try:
            response = requests.get(
                f'{self.api_url}/transactions/{transaction_id}/verify',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FlutterwavePaymentError(f'Failed to verify payment: {str(e)}')
    
    def get_transaction(self, transaction_id):
        """Get transaction details"""
        try:
            response = requests.get(
                f'{self.api_url}/transactions/{transaction_id}',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FlutterwavePaymentError(f'Failed to get transaction: {str(e)}')
    
    def refund_transaction(self, transaction_id, amount=None):
        """Refund a transaction"""
        try:
            data = {'id': transaction_id}
            if amount:
                data['amount'] = amount
                
            response = requests.post(
                f'{self.api_url}/transactions/{transaction_id}/refund',
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FlutterwavePaymentError(f'Failed to refund transaction: {str(e)}')
    
    def get_transactions(self, **filters):
        """Get list of transactions with optional filters"""
        try:
            response = requests.get(
                f'{self.api_url}/transactions',
                headers=self.headers,
                params=filters
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FlutterwavePaymentError(f'Failed to get transactions: {str(e)}') 