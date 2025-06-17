import json
import hmac
import hashlib
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from api.models import Order, Payment

class PayoneerWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('payoneer_webhook')
        
        # Create test order and payment
        self.order = Order.objects.create(
            id='test-order-1',
            status='PENDING',
            total_amount=100.00
        )
        self.payment = Payment.objects.create(
            id='test-payment-1',
            order=self.order,
            status='PENDING',
            amount=100.00
        )
        
        # Test payload
        self.payload = {
            'payment_id': 'test-payment-1',
            'order_id': 'test-order-1',
            'status': 'COMPLETED',
            'amount': 100.00,
            'currency': 'USD'
        }
        
        # Generate valid signature
        self.signature = hmac.new(
            settings.PAYONEER_WEBHOOK_SECRET.encode(),
            json.dumps(self.payload).encode(),
            hashlib.sha256
        ).hexdigest()

    def test_successful_webhook(self):
        """Test successful webhook processing"""
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(self.payload),
            content_type='application/json',
            HTTP_X_PAYONEER_SIGNATURE=self.signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify order and payment status updated
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        
        self.assertEqual(self.order.status, 'PAID')
        self.assertEqual(self.payment.status, 'COMPLETED')

    def test_invalid_signature(self):
        """Test webhook with invalid signature"""
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(self.payload),
            content_type='application/json',
            HTTP_X_PAYONEER_SIGNATURE='invalid-signature'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Verify order and payment status unchanged
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        
        self.assertEqual(self.order.status, 'PENDING')
        self.assertEqual(self.payment.status, 'PENDING')

    def test_missing_signature(self):
        """Test webhook with missing signature header"""
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(self.payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_invalid_payload(self):
        """Test webhook with invalid payload"""
        invalid_payload = {
            'payment_id': 'test-payment-1',
            'order_id': 'test-order-1'
            # Missing required fields
        }
        
        signature = hmac.new(
            settings.PAYONEER_WEBHOOK_SECRET.encode(),
            json.dumps(invalid_payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(invalid_payload),
            content_type='application/json',
            HTTP_X_PAYONEER_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 400)

    def test_non_completed_payment(self):
        """Test webhook with non-completed payment status"""
        payload = self.payload.copy()
        payload['status'] = 'PENDING'
        
        signature = hmac.new(
            settings.PAYONEER_WEBHOOK_SECRET.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_PAYONEER_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify order and payment status unchanged
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        
        self.assertEqual(self.order.status, 'PENDING')
        self.assertEqual(self.payment.status, 'PENDING')

    def test_order_not_found(self):
        """Test webhook with non-existent order"""
        payload = self.payload.copy()
        payload['order_id'] = 'non-existent-order'
        
        signature = hmac.new(
            settings.PAYONEER_WEBHOOK_SECRET.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_PAYONEER_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 404)

    def test_failed_payment(self):
        """Test webhook with failed payment status"""
        payload = self.payload.copy()
        payload['status'] = 'FAILED'
        
        signature = hmac.new(
            settings.PAYONEER_WEBHOOK_SECRET.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_PAYONEER_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify order and payment status updated
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        
        self.assertEqual(self.order.status, 'PAYMENT_FAILED')
        self.assertEqual(self.payment.status, 'FAILED') 