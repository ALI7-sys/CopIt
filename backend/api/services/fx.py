import logging
from typing import Dict, Optional, Tuple, List
from decimal import Decimal
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from .models import FXTransaction

logger = logging.getLogger(__name__)

class FXServiceError(Exception):
    """Base exception for FX service errors"""
    pass

class InsufficientBalanceError(FXServiceError):
    """Raised when there are insufficient funds for conversion"""
    pass

class InvalidRateError(FXServiceError):
    """Raised when the exchange rate is invalid"""
    pass

class BatchConversionError(FXServiceError):
    """Raised when batch conversion fails"""
    pass

class FXService:
    """Service for handling foreign exchange operations with Payoneer"""
    
    BASE_URL = 'https://api.payoneer.com/v1'
    SOURCE_CURRENCY = 'NGN'
    TARGET_CURRENCY = 'USD'
    RATE_CACHE_KEY = 'fx_rate_ngn_usd'
    RATE_CACHE_TTL = 300  # 5 minutes in seconds
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.default_headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and raise appropriate errors"""
        if response.status_code == 401:
            raise FXServiceError('Invalid API credentials')
        elif response.status_code == 403:
            raise FXServiceError('Insufficient permissions')
        elif response.status_code >= 500:
            raise FXServiceError('Payoneer API error')
        
        try:
            return response.json()
        except ValueError:
            raise FXServiceError('Invalid response from Payoneer API')

    def get_usd_balance(self) -> Decimal:
        """
        Get current USD balance from Payoneer
        
        Returns:
            Decimal: Current USD balance
        
        Raises:
            FXServiceError: If balance check fails
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/balances',
                headers=self.default_headers,
                params={'currency': self.TARGET_CURRENCY}
            )
            
            data = self._handle_response(response)
            return Decimal(str(data['available_balance']))
        except Exception as e:
            raise FXServiceError(f"Failed to get USD balance: {str(e)}")

    def get_exchange_rate(self, amount: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Get best available exchange rate for NGN to USD conversion
        Uses caching to minimize API calls
        
        Args:
            amount: Amount in NGN to convert
        
        Returns:
            Tuple[Decimal, Decimal]: (exchange_rate, fee)
        
        Raises:
            FXServiceError: If rate check fails
            InvalidRateError: If rate is invalid
        """
        try:
            # Try to get rate from cache first
            cached_data = cache.get(self.RATE_CACHE_KEY)
            if cached_data:
                rate, fee, timestamp = cached_data
                # Check if cache is still valid
                if datetime.utcnow() - timestamp < timedelta(seconds=self.RATE_CACHE_TTL):
                    return rate, fee
            
            # If not in cache or expired, fetch from API
            response = requests.get(
                f'{self.BASE_URL}/fx/rates',
                headers=self.default_headers,
                params={
                    'source_currency': self.SOURCE_CURRENCY,
                    'target_currency': self.TARGET_CURRENCY,
                    'amount': str(amount)
                }
            )
            
            data = self._handle_response(response)
            rate = Decimal(str(data['rate']))
            fee = Decimal(str(data['fee']))
            
            if rate <= 0:
                raise InvalidRateError('Invalid exchange rate received')
            
            # Cache the rate
            cache.set(
                self.RATE_CACHE_KEY,
                (rate, fee, datetime.utcnow()),
                self.RATE_CACHE_TTL
            )
            
            return rate, fee
        except Exception as e:
            raise FXServiceError(f"Failed to get exchange rate: {str(e)}")

    def convert_currency(self, ngn_amount: Decimal) -> Dict:
        """
        Convert NGN to USD at best available rate
        
        Args:
            ngn_amount: Amount in NGN to convert
        
        Returns:
            Dict: Conversion details including rate, fee, and converted amount
        
        Raises:
            FXServiceError: If conversion fails
            InsufficientBalanceError: If insufficient USD balance
        """
        try:
            # Check USD balance first
            usd_balance = self.get_usd_balance()
            
            # Get best available rate
            rate, fee = self.get_exchange_rate(ngn_amount)
            
            # Calculate converted amount
            converted_amount = (ngn_amount * rate) - fee
            
            # Verify sufficient balance
            if converted_amount > usd_balance:
                raise InsufficientBalanceError(
                    f"Insufficient USD balance. Required: {converted_amount}, Available: {usd_balance}"
                )
            
            # Execute conversion
            response = requests.post(
                f'{self.BASE_URL}/fx/convert',
                headers=self.default_headers,
                json={
                    'source_currency': self.SOURCE_CURRENCY,
                    'target_currency': self.TARGET_CURRENCY,
                    'amount': str(ngn_amount),
                    'rate': str(rate)
                }
            )
            
            data = self._handle_response(response)
            
            # Log FX transaction
            self._log_fx_transaction(
                ngn_amount=ngn_amount,
                usd_amount=converted_amount,
                rate=rate,
                fee=fee,
                transaction_id=data['transaction_id']
            )
            
            return {
                'transaction_id': data['transaction_id'],
                'source_amount': ngn_amount,
                'target_amount': converted_amount,
                'rate': rate,
                'fee': fee,
                'status': 'completed'
            }
            
        except InsufficientBalanceError:
            raise
        except Exception as e:
            raise FXServiceError(f"Failed to convert currency: {str(e)}")

    def batch_convert_currency(self, amounts: List[Decimal]) -> List[Dict]:
        """
        Convert multiple NGN amounts to USD in a single batch
        
        Args:
            amounts: List of NGN amounts to convert
        
        Returns:
            List[Dict]: List of conversion results
        
        Raises:
            BatchConversionError: If batch conversion fails
            InsufficientBalanceError: If insufficient USD balance
        """
        try:
            if not amounts:
                return []
            
            # Get total required USD balance
            total_converted = Decimal('0')
            conversions = []
            
            # Get rate once for all conversions
            rate, fee = self.get_exchange_rate(sum(amounts))
            
            # Calculate all conversions
            for amount in amounts:
                converted = (amount * rate) - fee
                total_converted += converted
                conversions.append({
                    'source_amount': amount,
                    'target_amount': converted,
                    'rate': rate,
                    'fee': fee
                })
            
            # Check if we have enough balance
            usd_balance = self.get_usd_balance()
            if total_converted > usd_balance:
                raise InsufficientBalanceError(
                    f"Insufficient USD balance. Required: {total_converted}, Available: {usd_balance}"
                )
            
            # Execute batch conversion
            response = requests.post(
                f'{self.BASE_URL}/fx/batch-convert',
                headers=self.default_headers,
                json={
                    'conversions': [
                        {
                            'source_currency': self.SOURCE_CURRENCY,
                            'target_currency': self.TARGET_CURRENCY,
                            'amount': str(conv['source_amount']),
                            'rate': str(rate)
                        }
                        for conv in conversions
                    ]
                }
            )
            
            data = self._handle_response(response)
            transaction_ids = data['transaction_ids']
            
            # Log all transactions
            results = []
            for i, (conv, tx_id) in enumerate(zip(conversions, transaction_ids)):
                self._log_fx_transaction(
                    ngn_amount=conv['source_amount'],
                    usd_amount=conv['target_amount'],
                    rate=conv['rate'],
                    fee=conv['fee'],
                    transaction_id=tx_id
                )
                
                results.append({
                    'transaction_id': tx_id,
                    'source_amount': conv['source_amount'],
                    'target_amount': conv['target_amount'],
                    'rate': conv['rate'],
                    'fee': conv['fee'],
                    'status': 'completed'
                })
            
            return results
            
        except InsufficientBalanceError:
            raise
        except Exception as e:
            raise BatchConversionError(f"Failed to process batch conversion: {str(e)}")

    def _log_fx_transaction(
        self,
        ngn_amount: Decimal,
        usd_amount: Decimal,
        rate: Decimal,
        fee: Decimal,
        transaction_id: str
    ) -> None:
        """
        Log FX transaction details for accounting
        
        Args:
            ngn_amount: Original amount in NGN
            usd_amount: Converted amount in USD
            rate: Exchange rate used
            fee: FX fee charged
            transaction_id: Payoneer transaction ID
        """
        try:
            FXTransaction.objects.create(
                transaction_id=transaction_id,
                source_currency=self.SOURCE_CURRENCY,
                target_currency=self.TARGET_CURRENCY,
                source_amount=ngn_amount,
                target_amount=usd_amount,
                exchange_rate=rate,
                fee=fee,
                timestamp=datetime.utcnow()
            )
            
            logger.info(
                f"FX Transaction logged - ID: {transaction_id}, "
                f"Amount: {ngn_amount} {self.SOURCE_CURRENCY} → {usd_amount} {self.TARGET_CURRENCY}, "
                f"Rate: {rate}, Fee: {fee}"
            )
        except Exception as e:
            logger.error(f"Failed to log FX transaction: {str(e)}")

# Create a singleton instance
fx_service = FXService(api_key=settings.PAYONEER_API_KEY) 