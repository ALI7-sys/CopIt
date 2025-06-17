from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..services.vcc_service import vcc_service, VCCServiceError, CardNotFoundError, InsufficientBalanceError
from ..middleware import require_auth, rate_limit, handle_api_errors

# Rate limit settings
CARD_CREATE_LIMIT = 10  # 10 cards per hour
CARD_LIST_LIMIT = 60    # 60 requests per minute
CARD_DETAIL_LIMIT = 30  # 30 requests per minute

@csrf_exempt
@require_http_methods(['POST'])
@require_auth
@rate_limit('card_create', CARD_CREATE_LIMIT, 3600)  # 1 hour
@handle_api_errors
def create_card(request):
    """Create a new virtual card"""
    try:
        data = request.json
        amount = Decimal(str(data.get('amount', 0)))
        merchant = data.get('merchant')
        description = data.get('description')
        
        if not merchant:
            return JsonResponse({
                'status': 'failed',
                'error': 'Merchant is required',
                'error_type': 'validation_error'
            }, status=400)
        
        card = vcc_service.create_virtual_card(
            amount=amount,
            merchant=merchant,
            description=description
        )
        
        return JsonResponse({
            'status': 'success',
            'data': card
        })
        
    except InsufficientBalanceError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'insufficient_balance'
        }, status=400)
    except VCCServiceError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'failed',
            'error': 'Internal server error',
            'error_type': 'server_error'
        }, status=500)

@require_http_methods(['GET'])
@require_auth
@rate_limit('card_detail', CARD_DETAIL_LIMIT, 60)  # 1 minute
@handle_api_errors
def get_card(request, card_id: str):
    """Get details for a specific card"""
    try:
        card = vcc_service.get_card_details(card_id)
        return JsonResponse({
            'status': 'success',
            'data': card
        })
    except CardNotFoundError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_not_found'
        }, status=404)
    except VCCServiceError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'failed',
            'error': 'Internal server error',
            'error_type': 'server_error'
        }, status=500)

@require_http_methods(['GET'])
@require_auth
@rate_limit('card_list', CARD_LIST_LIMIT, 60)  # 1 minute
@handle_api_errors
def list_cards(request):
    """List all active cards"""
    try:
        cards = vcc_service.list_active_cards()
        return JsonResponse({
            'status': 'success',
            'data': cards
        })
    except VCCServiceError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'failed',
            'error': 'Internal server error',
            'error_type': 'server_error'
        }, status=500)

@csrf_exempt
@require_http_methods(['POST'])
@require_auth
@rate_limit('card_cancel', CARD_DETAIL_LIMIT, 60)  # 1 minute
@handle_api_errors
def cancel_card(request, card_id: str):
    """Cancel a virtual card"""
    try:
        result = vcc_service.cancel_card(card_id)
        return JsonResponse({
            'status': 'success',
            'data': result
        })
    except CardNotFoundError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_not_found'
        }, status=404)
    except VCCServiceError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'failed',
            'error': 'Internal server error',
            'error_type': 'server_error'
        }, status=500)

@require_http_methods(['GET'])
@require_auth
@rate_limit('card_transactions', CARD_DETAIL_LIMIT, 60)  # 1 minute
@handle_api_errors
def get_card_transactions(request, card_id: str):
    """Get transactions for a specific card"""
    try:
        # Parse date filters if provided
        start_date = None
        end_date = None
        
        if 'start_date' in request.GET:
            start_date = datetime.fromisoformat(request.GET['start_date'])
        if 'end_date' in request.GET:
            end_date = datetime.fromisoformat(request.GET['end_date'])
        
        transactions = vcc_service.get_card_transactions(
            card_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return JsonResponse({
            'status': 'success',
            'data': transactions
        })
    except CardNotFoundError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_not_found'
        }, status=404)
    except VCCServiceError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_error'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'status': 'failed',
            'error': 'Invalid date format',
            'error_type': 'validation_error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'failed',
            'error': 'Internal server error',
            'error_type': 'server_error'
        }, status=500)

@require_http_methods(['GET'])
@require_auth
@rate_limit('card_stats', CARD_DETAIL_LIMIT, 60)  # 1 minute
@handle_api_errors
def get_card_stats(request, card_id: str):
    """Get usage statistics for a specific card"""
    try:
        stats = vcc_service.get_card_usage_stats(card_id)
        return JsonResponse({
            'status': 'success',
            'data': stats
        })
    except CardNotFoundError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_not_found'
        }, status=404)
    except VCCServiceError as e:
        return JsonResponse({
            'status': 'failed',
            'error': str(e),
            'error_type': 'card_error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'failed',
            'error': 'Internal server error',
            'error_type': 'server_error'
        }, status=500) 