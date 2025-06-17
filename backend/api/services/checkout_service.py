from typing import Dict, List, Optional
from decimal import Decimal
from .order_calculator import order_calculator
from .revolut_service import revolut_service, RevolutServiceError, InvalidAPIVersionError, CardNotFoundError

class CheckoutError(Exception):
    """Base exception for checkout service errors"""
    pass

class PaymentError(CheckoutError):
    """Raised when payment processing fails"""
    pass

class CheckoutService:
    def __init__(self):
        self.order_calculator = order_calculator
        self.payment_service = revolut_service

    def process_checkout(self,
                        items: List[Dict],
                        shipping_address: Dict,
                        payment_card_id: str) -> Dict:
        """
        Process a complete checkout including order calculations and payment
        
        Args:
            items: List of items in the order
            shipping_address: Customer's shipping address
            payment_card_id: ID of the payment card to use
        
        Returns:
            Dict containing order and payment details
        
        Raises:
            CheckoutError: If checkout processing fails
            PaymentError: If payment processing fails
            InvalidAPIVersionError: If API version is invalid
            CardNotFoundError: If payment card is not found
        """
        try:
            # Calculate order totals
            subtotal = sum(
                Decimal(item['price']) * item['quantity']
                for item in items
            )
            
            order_totals = self.order_calculator.calculate_order_totals(
                subtotal=subtotal,
                items=items,
                shipping_address=shipping_address
            )

            try:
                # Process payment
                payment = self.payment_service.process_transaction(
                    card_id=payment_card_id,
                    amount=int(order_totals['total'] * 100),  # Convert to cents
                    merchant="CopIt Store",
                    description=f"Order total: ${order_totals['total']}"
                )

                # Create order record
                order = {
                    'items': items,
                    'totals': order_totals,
                    'shipping_address': shipping_address,
                    'payment': {
                        'card_id': payment_card_id,
                        'transaction_id': payment['id'],
                        'status': payment['status']
                    }
                }

                return {
                    'order': order,
                    'payment': payment,
                    'status': 'success' if payment['status'] == 'approved' else 'failed'
                }

            except InvalidAPIVersionError as e:
                raise PaymentError(f"Payment service API version error: {str(e)}")
            except CardNotFoundError as e:
                raise PaymentError(f"Payment card not found: {str(e)}")
            except RevolutServiceError as e:
                raise PaymentError(f"Payment processing failed: {str(e)}")

        except Exception as e:
            raise CheckoutError(f"Checkout processing failed: {str(e)}")

    def get_order_summary(self,
                         items: List[Dict],
                         shipping_address: Optional[Dict] = None) -> Dict:
        """
        Get order summary with calculated totals before payment
        
        Args:
            items: List of items in the order
            shipping_address: Optional shipping address for shipping calculations
        
        Returns:
            Dict containing order summary and calculated totals
        
        Raises:
            CheckoutError: If order summary calculation fails
        """
        try:
            subtotal = sum(
                Decimal(item['price']) * item['quantity']
                for item in items
            )
            
            return self.order_calculator.calculate_order_totals(
                subtotal=subtotal,
                items=items,
                shipping_address=shipping_address
            )
        except Exception as e:
            raise CheckoutError(f"Failed to calculate order summary: {str(e)}")

# Create a singleton instance
checkout_service = CheckoutService() 