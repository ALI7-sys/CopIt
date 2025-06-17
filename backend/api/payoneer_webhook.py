import hmac
import hashlib
import json
from typing import Dict, Optional
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Order, Payment
from .services.revolut_service import RevolutServiceError

class PayoneerWebhookError(Exception):
    """Base exception for Payoneer webhook errors"""
    pass

class InvalidSignatureError(PayoneerWebhookError):
    """Raised when webhook signature validation fails"""
    pass

class InvalidPayloadError(PayoneerWebhookError):
    """Raised when webhook payload is invalid"""
    pass

def validate_signature(payload: bytes, signature: str) -> bool:
    """
    Validate Payoneer webhook signature
    
    Args:
        payload: Raw request body
        signature: Payoneer signature from X-Payoneer-Signature header
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        expected_signature = hmac.new(
            settings.PAYONEER_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        raise InvalidSignatureError(f"Failed to validate signature: {str(e)}")

def parse_payload(payload: bytes) -> Dict:
    """
    Parse and validate webhook payload
    
    Args:
        payload: Raw request body
    
    Returns:
        Dict: Parsed payload
    
    Raises:
        InvalidPayloadError: If payload is invalid
    """
    try:
        data = json.loads(payload)
        
        # Validate required fields
        required_fields = ['payment_id', 'status', 'amount', 'currency', 'order_id']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise InvalidPayloadError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return data
    except json.JSONDecodeError as e:
        raise InvalidPayloadError(f"Invalid JSON payload: {str(e)}")

def update_order_status(order_id: str, payment_id: str, status: str) -> None:
    """
    Update order and payment status in database
    
    Args:
        order_id: Order ID
        payment_id: Payment ID
        status: Payment status
    
    Raises:
        Order.DoesNotExist: If order is not found
    """
    try:
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(id=payment_id)
        
        if status == 'COMPLETED':
            order.status = 'PAID'
            payment.status = 'COMPLETED'
        else:
            order.status = 'PAYMENT_FAILED'
            payment.status = 'FAILED'
        
        order.save()
        payment.save()
    except Order.DoesNotExist:
        raise
    except Exception as e:
        raise PayoneerWebhookError(f"Failed to update order status: {str(e)}")

@csrf_exempt
@require_POST
def payoneer_webhook(request: HttpRequest) -> HttpResponse:
    """
    Handle Payoneer webhook notifications
    
    Args:
        request: HTTP request object
    
    Returns:
        HttpResponse: 200 OK if successful, 400 Bad Request if validation fails
    """
    try:
        # Get signature from header
        signature = request.headers.get('X-Payoneer-Signature')
        if not signature:
            return HttpResponse('Missing signature', status=400)
        
        # Validate signature
        if not validate_signature(request.body, signature):
            return HttpResponse('Invalid signature', status=400)
        
        # Parse and validate payload
        payload = parse_payload(request.body)
        
        # Only process completed payments
        if payload['status'] != 'COMPLETED':
            return HttpResponse('Ignoring non-completed payment', status=200)
        
        # Update order status
        update_order_status(
            order_id=payload['order_id'],
            payment_id=payload['payment_id'],
            status=payload['status']
        )
        
        return HttpResponse('Webhook processed successfully', status=200)
        
    except InvalidSignatureError as e:
        return HttpResponse(str(e), status=400)
    except InvalidPayloadError as e:
        return HttpResponse(str(e), status=400)
    except Order.DoesNotExist:
        return HttpResponse('Order not found', status=404)
    except Exception as e:
        return HttpResponse(f'Internal server error: {str(e)}', status=500) 