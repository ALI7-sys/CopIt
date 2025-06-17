import pytest
from decimal import Decimal
from api.services.checkout_service import checkout_service
from api.services.privacy_service import PrivacyServiceError

def test_successful_checkout():
    # Create test data
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '25.00', 'quantity': 2},
        {'id': '2', 'name': 'Product 2', 'price': '15.00', 'quantity': 1}
    ]
    shipping_address = {
        'street': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip': '12345',
        'country': 'US'
    }
    payment_card_id = 'test-card-1'

    # Process checkout
    result = checkout_service.process_checkout(
        items=items,
        shipping_address=shipping_address,
        payment_card_id=payment_card_id
    )

    # Verify result
    assert result['status'] == 'success'
    assert 'order' in result
    assert 'payment' in result
    
    # Verify order totals
    order = result['order']
    totals = order['totals']
    assert totals['subtotal'] == Decimal('65.00')  # (25.00 * 2) + 15.00
    assert totals['fulfillment_commission'] == Decimal('1.30')  # 2% of 65.00
    assert totals['shipping_fee'] == Decimal('5.99')  # Base shipping fee
    assert totals['total'] == Decimal('72.29')  # 65.00 + 1.30 + 5.99

    # Verify payment details
    payment = result['payment']
    assert payment['status'] == 'approved'
    assert payment['amount'] == 7229  # 72.29 in cents
    assert payment['merchant'] == 'CopIt Store'

def test_failed_payment():
    # Create test data
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '25.00', 'quantity': 1}
    ]
    shipping_address = {
        'street': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip': '12345',
        'country': 'US'
    }
    payment_card_id = 'invalid-card'

    # Process checkout
    result = checkout_service.process_checkout(
        items=items,
        shipping_address=shipping_address,
        payment_card_id=payment_card_id
    )

    # Verify result
    assert result['status'] == 'failed'
    assert 'error' in result
    assert 'order_totals' in result

    # Verify order totals are still calculated
    totals = result['order_totals']
    assert totals['subtotal'] == Decimal('25.00')
    assert totals['fulfillment_commission'] == Decimal('0.50')  # 2% of 25.00
    assert totals['shipping_fee'] == Decimal('5.99')  # Base shipping fee
    assert totals['total'] == Decimal('31.49')  # 25.00 + 0.50 + 5.99

def test_order_summary():
    # Create test data
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '25.00', 'quantity': 2},
        {'id': '2', 'name': 'Product 2', 'price': '15.00', 'quantity': 1}
    ]
    shipping_address = {
        'street': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip': '12345',
        'country': 'US'
    }

    # Get order summary
    summary = checkout_service.get_order_summary(
        items=items,
        shipping_address=shipping_address
    )

    # Verify summary
    assert summary['subtotal'] == Decimal('65.00')  # (25.00 * 2) + 15.00
    assert summary['fulfillment_commission'] == Decimal('1.30')  # 2% of 65.00
    assert summary['shipping_fee'] == Decimal('5.99')  # Base shipping fee
    assert summary['total'] == Decimal('72.29')  # 65.00 + 1.30 + 5.99
    assert 'breakdown' in summary

def test_free_shipping_checkout():
    # Create test data with order over free shipping threshold
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '60.00', 'quantity': 1}
    ]
    shipping_address = {
        'street': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip': '12345',
        'country': 'US'
    }
    payment_card_id = 'test-card-1'

    # Process checkout
    result = checkout_service.process_checkout(
        items=items,
        shipping_address=shipping_address,
        payment_card_id=payment_card_id
    )

    # Verify result
    assert result['status'] == 'success'
    
    # Verify order totals
    order = result['order']
    totals = order['totals']
    assert totals['subtotal'] == Decimal('60.00')
    assert totals['fulfillment_commission'] == Decimal('1.20')  # 2% of 60.00
    assert totals['shipping_fee'] == Decimal('0.00')  # Free shipping
    assert totals['total'] == Decimal('61.20')  # 60.00 + 1.20

    # Verify payment amount
    payment = result['payment']
    assert payment['amount'] == 6120  # 61.20 in cents 