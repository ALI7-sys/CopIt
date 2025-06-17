from typing import Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP

class OrderCalculator:
    FULFILLMENT_COMMISSION_RATE = Decimal('0.02')  # 2%
    BASE_SHIPPING_FEE = Decimal('5.99')  # Base shipping fee
    FREE_SHIPPING_THRESHOLD = Decimal('50.00')  # Free shipping over $50

    @classmethod
    def calculate_order_totals(cls, 
                             subtotal: Decimal,
                             items: List[Dict],
                             shipping_address: Optional[Dict] = None) -> Dict:
        """
        Calculate all order totals including commission and shipping
        
        Args:
            subtotal: Order subtotal before fees
            items: List of items in the order
            shipping_address: Optional shipping address for distance-based calculations
        
        Returns:
            Dict containing all calculated totals
        """
        # Calculate fulfillment commission
        fulfillment_commission = (subtotal * cls.FULFILLMENT_COMMISSION_RATE).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )

        # Calculate shipping fee
        shipping_fee = cls._calculate_shipping_fee(subtotal, shipping_address)

        # Calculate total
        total = subtotal + fulfillment_commission + shipping_fee

        return {
            'subtotal': subtotal,
            'fulfillment_commission': fulfillment_commission,
            'shipping_fee': shipping_fee,
            'total': total,
            'breakdown': {
                'items': items,
                'fulfillment_rate': float(cls.FULFILLMENT_COMMISSION_RATE),
                'shipping_threshold': float(cls.FREE_SHIPPING_THRESHOLD)
            }
        }

    @classmethod
    def _calculate_shipping_fee(cls, 
                              subtotal: Decimal,
                              shipping_address: Optional[Dict] = None) -> Decimal:
        """
        Calculate shipping fee based on order total and shipping address
        
        Args:
            subtotal: Order subtotal
            shipping_address: Optional shipping address for distance-based calculations
        
        Returns:
            Calculated shipping fee
        """
        # Free shipping for orders over threshold
        if subtotal >= cls.FREE_SHIPPING_THRESHOLD:
            return Decimal('0.00')

        # Base shipping fee
        shipping_fee = cls.BASE_SHIPPING_FEE

        # Add distance-based fee if shipping address provided
        if shipping_address:
            # TODO: Implement distance-based shipping calculations
            # For now, just return base shipping fee
            pass

        return shipping_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# Create a singleton instance
order_calculator = OrderCalculator() 