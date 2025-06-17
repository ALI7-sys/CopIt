from flask import Blueprint, request, jsonify
from ..services.checkout_service import checkout_service, CheckoutError, PaymentError
from ..services.privacy_service import PrivacyServiceError, InvalidAPIVersionError, CardNotFoundError

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/api/checkout/summary', methods=['POST'])
def get_order_summary():
    try:
        data = request.get_json()
        items = data.get('items', [])
        shipping_address = data.get('shipping_address')

        if not items:
            return jsonify({'error': 'No items provided'}), 400

        summary = checkout_service.get_order_summary(
            items=items,
            shipping_address=shipping_address
        )

        return jsonify(summary)
    except CheckoutError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@checkout_bp.route('/api/checkout/process', methods=['POST'])
def process_checkout():
    try:
        data = request.get_json()
        items = data.get('items', [])
        shipping_address = data.get('shipping_address')
        payment_card_id = data.get('payment_card_id')

        if not all([items, shipping_address, payment_card_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        result = checkout_service.process_checkout(
            items=items,
            shipping_address=shipping_address,
            payment_card_id=payment_card_id
        )

        if result['status'] == 'failed':
            return jsonify(result), 400

        return jsonify(result)
    except PaymentError as e:
        return jsonify({
            'status': 'failed',
            'error': str(e),
            'error_type': 'payment_error'
        }), 400
    except InvalidAPIVersionError as e:
        return jsonify({
            'status': 'failed',
            'error': str(e),
            'error_type': 'api_version_error'
        }), 400
    except CardNotFoundError as e:
        return jsonify({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_not_found'
        }), 404
    except CheckoutError as e:
        return jsonify({
            'status': 'failed',
            'error': str(e),
            'error_type': 'checkout_error'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'failed',
            'error': 'Internal server error',
            'error_type': 'server_error'
        }), 500 