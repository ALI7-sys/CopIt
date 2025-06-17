import pytest
from decimal import Decimal
from api.services.order_calculator import order_calculator

def test_basic_order_calculation():
    # Test order under free shipping threshold
    subtotal = Decimal('25.00')
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '15.00', 'quantity': 1},
        {'id': '2', 'name': 'Product 2', 'price': '10.00', 'quantity': 1}
    ]

    totals = order_calculator.calculate_order_totals(subtotal, items)

    assert totals['subtotal'] == Decimal('25.00')
    assert totals['fulfillment_commission'] == Decimal('0.50')  # 2% of $25.00
    assert totals['shipping_fee'] == Decimal('5.99')  # Base shipping fee
    assert totals['total'] == Decimal('31.49')  # $25.00 + $0.50 + $5.99

def test_free_shipping_threshold():
    # Test order over free shipping threshold
    subtotal = Decimal('75.00')
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '75.00', 'quantity': 1}
    ]

    totals = order_calculator.calculate_order_totals(subtotal, items)

    assert totals['subtotal'] == Decimal('75.00')
    assert totals['fulfillment_commission'] == Decimal('1.50')  # 2% of $75.00
    assert totals['shipping_fee'] == Decimal('0.00')  # Free shipping
    assert totals['total'] == Decimal('76.50')  # $75.00 + $1.50

def test_exact_free_shipping_threshold():
    # Test order exactly at free shipping threshold
    subtotal = Decimal('50.00')
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '50.00', 'quantity': 1}
    ]

    totals = order_calculator.calculate_order_totals(subtotal, items)

    assert totals['subtotal'] == Decimal('50.00')
    assert totals['fulfillment_commission'] == Decimal('1.00')  # 2% of $50.00
    assert totals['shipping_fee'] == Decimal('0.00')  # Free shipping
    assert totals['total'] == Decimal('51.00')  # $50.00 + $1.00

def test_multiple_quantity_items():
    # Test order with multiple quantities
    subtotal = Decimal('45.00')
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '15.00', 'quantity': 3}
    ]

    totals = order_calculator.calculate_order_totals(subtotal, items)

    assert totals['subtotal'] == Decimal('45.00')
    assert totals['fulfillment_commission'] == Decimal('0.90')  # 2% of $45.00
    assert totals['shipping_fee'] == Decimal('5.99')  # Base shipping fee
    assert totals['total'] == Decimal('51.89')  # $45.00 + $0.90 + $5.99

def test_rounding():
    # Test rounding behavior
    subtotal = Decimal('33.33')
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '33.33', 'quantity': 1}
    ]

    totals = order_calculator.calculate_order_totals(subtotal, items)

    assert totals['subtotal'] == Decimal('33.33')
    assert totals['fulfillment_commission'] == Decimal('0.67')  # 2% of $33.33, rounded up
    assert totals['shipping_fee'] == Decimal('5.99')  # Base shipping fee
    assert totals['total'] == Decimal('39.99')  # $33.33 + $0.67 + $5.99

def test_breakdown_information():
    # Test that breakdown information is included
    subtotal = Decimal('25.00')
    items = [
        {'id': '1', 'name': 'Product 1', 'price': '25.00', 'quantity': 1}
    ]

    totals = order_calculator.calculate_order_totals(subtotal, items)

    assert 'breakdown' in totals
    assert totals['breakdown']['items'] == items
    assert totals['breakdown']['fulfillment_rate'] == 0.02
    assert totals['breakdown']['shipping_threshold'] == 50.00 