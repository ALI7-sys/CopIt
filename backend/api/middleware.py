import time
from typing import Callable
from django.http import JsonResponse, HttpRequest
from django.core.cache import cache
from django.conf import settings
from functools import wraps

class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass

def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'unknown')

def rate_limit(
    key_prefix: str,
    limit: int = 60,
    period: int = 60
) -> Callable:
    """
    Rate limiting decorator
    
    Args:
        key_prefix: Prefix for cache key
        limit: Number of requests allowed in period
        period: Time period in seconds
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args, **kwargs):
            # Get client identifier (IP or user ID)
            client_id = get_client_ip(request)
            if request.user.is_authenticated:
                client_id = f"user_{request.user.id}"
            
            # Create cache key
            cache_key = f"rate_limit:{key_prefix}:{client_id}"
            
            # Get current count
            current = cache.get(cache_key, 0)
            
            if current >= limit:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Maximum {limit} requests per {period} seconds."
                )
            
            # Increment counter
            cache.set(cache_key, current + 1, period)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def require_auth(view_func: Callable) -> Callable:
    """Authentication decorator"""
    @wraps(view_func)
    def wrapped_view(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'failed',
                'error': 'Authentication required',
                'error_type': 'auth_error'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

def handle_api_errors(view_func: Callable) -> Callable:
    """Error handling decorator"""
    @wraps(view_func)
    def wrapped_view(request: HttpRequest, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except RateLimitExceeded as e:
            return JsonResponse({
                'status': 'failed',
                'error': str(e),
                'error_type': 'rate_limit_exceeded'
            }, status=429)
        except Exception as e:
            return JsonResponse({
                'status': 'failed',
                'error': 'Internal server error',
                'error_type': 'server_error'
            }, status=500)
    return wrapped_view 