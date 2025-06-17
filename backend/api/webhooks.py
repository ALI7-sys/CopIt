from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
import hmac
import hashlib
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PrivacyWebhookView(APIView):
    permission_classes = [AllowAny]  # Privacy.com needs to access this endpoint without auth

    def verify_signature(self, request):
        """Verify the webhook signature from Privacy.com"""
        signature = request.headers.get('X-Privacy-Signature')
        if not signature:
            return False

        # Get the raw request body
        body = request.body.decode('utf-8')
        
        # Create HMAC using the webhook secret
        expected_signature = hmac.new(
            settings.PRIVACY_WEBHOOK_SECRET.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def post(self, request):
        """Handle incoming Privacy.com webhook events"""
        if not self.verify_signature(request):
            logger.warning("Invalid webhook signature received")
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            event_data = json.loads(request.body)
            event_type = event_data.get('type')
            
            if event_type == 'card.approved':
                self._handle_card_approved(event_data)
            elif event_type == 'card.declined':
                self._handle_card_declined(event_data)
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            logger.error("Invalid JSON payload received")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_card_approved(self, event_data):
        """Handle approved card transaction"""
        try:
            card_id = event_data.get('card_id')
            amount = event_data.get('amount')
            merchant = event_data.get('merchant')
            
            # Update order status in database
            # TODO: Implement order status update logic
            logger.info(f"Card {card_id} approved for amount {amount} at {merchant}")
            
        except Exception as e:
            logger.error(f"Error handling card approval: {str(e)}")

    def _handle_card_declined(self, event_data):
        """Handle declined card transaction"""
        try:
            card_id = event_data.get('card_id')
            amount = event_data.get('amount')
            merchant = event_data.get('merchant')
            decline_reason = event_data.get('decline_reason')
            
            # Log fraud attempt
            logger.warning(
                f"Fraud attempt detected - Card: {card_id}, "
                f"Amount: {amount}, Merchant: {merchant}, "
                f"Reason: {decline_reason}"
            )
            
            # Update order status in database
            # TODO: Implement order status update logic
            
        except Exception as e:
            logger.error(f"Error handling card decline: {str(e)}") 