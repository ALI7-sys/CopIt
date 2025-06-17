from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import requests
from decimal import Decimal, ROUND_HALF_UP
import os
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Rate limit decorators
ONE_MINUTE = 60
GREY_RATE_LIMIT = int(os.getenv('GREY_API_RATE_LIMIT', '100'))
PRIVACY_RATE_LIMIT = int(os.getenv('PRIVACY_API_RATE_LIMIT', '50'))

class PaymentServiceError(Exception):
    """Base exception for payment service errors"""
    pass

class CurrencyConversionError(PaymentServiceError):
    """Raised when currency conversion fails"""
    pass

class VCCGenerationError(PaymentServiceError):
    """Raised when VCC generation fails"""
    pass

class PaymentService:
    def __init__(self):
        # Load API keys from environment variables
        self.grey_api_key = os.getenv('GREY_API_KEY')
        self.privacy_api_key = os.getenv('PRIVACY_API_KEY')
        
        # API endpoints
        self.grey_api_url = "https://api.grey.co/v1/convert"  # Mock URL
        self.privacy_api_url = "https://api.privacy.com/v1/card"  # Mock URL
        
        # Service fees
        self.service_fee_percentage = Decimal('0.02')  # 2%
        self.shipping_commission = Decimal('0.05')  # 5%

        # Validate API keys
        if not self.grey_api_key or not self.privacy_api_key:
            raise PaymentServiceError("API keys not found in environment variables")

    @sleep_and_retry
    @limits(calls=GREY_RATE_LIMIT, period=ONE_MINUTE)
    @retry(
        stop=stop_after_attempt(int(os.getenv('MAX_RETRIES', '3'))),
        wait=wait_exponential(multiplier=float(os.getenv('RETRY_DELAY', '1')))
    )
    def _convert_ngn_to_usd(self, ngn_amount: Decimal) -> Decimal:
        """
        Convert NGN to USD using Grey API with rate limiting and retries
        For now, using a mock conversion rate of 1 USD = 1000 NGN
        """
        try:
            # Mock API call
            # In production, replace with actual API call:
            # response = requests.get(
            #     self.grey_api_url,
            #     params={'from': 'NGN', 'to': 'USD', 'amount': str(ngn_amount)},
            #     headers={'Authorization': f'Bearer {self.grey_api_key}'}
            # )
            # response.raise_for_status()
            # return Decimal(response.json()['amount'])

            # Mock conversion
            mock_rate = Decimal('1000')  # 1 USD = 1000 NGN
            usd_amount = ngn_amount / mock_rate
            return usd_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        except requests.RequestException as e:
            raise CurrencyConversionError(f"Failed to convert currency: {str(e)}")
        except (KeyError, ValueError) as e:
            raise CurrencyConversionError(f"Invalid response from currency API: {str(e)}")

    def _calculate_fees(self, usd_amount: Decimal) -> Tuple[Decimal, Decimal]:
        """Calculate service fee and shipping commission"""
        service_fee = (usd_amount * self.service_fee_percentage).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        shipping_commission = (usd_amount * self.shipping_commission).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        return service_fee, shipping_commission

    @sleep_and_retry
    @limits(calls=PRIVACY_RATE_LIMIT, period=ONE_MINUTE)
    @retry(
        stop=stop_after_attempt(int(os.getenv('MAX_RETRIES', '3'))),
        wait=wait_exponential(multiplier=float(os.getenv('RETRY_DELAY', '1')))
    )
    def _generate_vcc(self, usd_amount: Decimal, merchant: str) -> Dict:
        """
        Generate a Privacy.com VCC with rate limiting and retries
        For now, using a mock response
        """
        try:
            # Mock API call
            # In production, replace with actual API call:
            # response = requests.post(
            #     self.privacy_api_url,
            #     json={
            #         'type': 'VIRTUAL',
            #         'spend_limit': str(usd_amount),
            #         'spend_limit_duration': 'TRANSACTION',
            #         'merchant_locked': merchant,
            #         'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            #     },
            #     headers={'Authorization': f'Bearer {self.privacy_api_key}'}
            # )
            # response.raise_for_status()
            # return response.json()

            # Mock response
            expiry = datetime.utcnow() + timedelta(hours=24)
            return {
                'token': f'mock_vcc_{merchant.lower()}_{expiry.timestamp()}',
                'expires_at': expiry.isoformat(),
                'spend_limit': str(usd_amount),
                'merchant_locked': merchant
            }

        except requests.RequestException as e:
            raise VCCGenerationError(f"Failed to generate VCC: {str(e)}")
        except (KeyError, ValueError) as e:
            raise VCCGenerationError(f"Invalid response from VCC API: {str(e)}")

    def process_payment(
        self, 
        ngn_amount: Decimal, 
        merchant: str
    ) -> Dict[str, any]:
        """
        Process payment by converting currency and generating VCC
        
        Args:
            ngn_amount: Amount in Nigerian Naira
            merchant: Merchant name (e.g., 'Back Market' or 'Newegg')
            
        Returns:
            Dict containing:
                - vcc_token: Generated VCC token
                - usd_amount: Amount in USD
                - service_fee: Service fee amount
                - shipping_commission: Shipping commission amount
                - total_amount: Total amount including fees
                - expires_at: VCC expiry timestamp
                
        Raises:
            PaymentServiceError: If any step of the process fails
        """
        try:
            # Convert NGN to USD
            usd_amount = self._convert_ngn_to_usd(ngn_amount)
            
            # Calculate fees
            service_fee, shipping_commission = self._calculate_fees(usd_amount)
            total_amount = usd_amount + service_fee + shipping_commission
            
            # Generate VCC
            vcc_data = self._generate_vcc(total_amount, merchant)
            
            return {
                'vcc_token': vcc_data['token'],
                'usd_amount': str(usd_amount),
                'service_fee': str(service_fee),
                'shipping_commission': str(shipping_commission),
                'total_amount': str(total_amount),
                'expires_at': vcc_data['expires_at'],
                'merchant': merchant
            }
            
        except (CurrencyConversionError, VCCGenerationError) as e:
            raise PaymentServiceError(f"Payment processing failed: {str(e)}")
        except Exception as e:
            raise PaymentServiceError(f"Unexpected error: {str(e)}")

# Example usage:
if __name__ == "__main__":
    try:
        payment_service = PaymentService()
        result = payment_service.process_payment(
            ngn_amount=Decimal('100000'),  # 100,000 NGN
            merchant='Back Market'
        )
        print("Payment processed successfully:")
        print(f"VCC Token: {result['vcc_token']}")
        print(f"USD Amount: ${result['usd_amount']}")
        print(f"Service Fee: ${result['service_fee']}")
        print(f"Shipping Commission: {result['shipping_commission']}")
        print(f"Total Amount: ${result['total_amount']}")
        print(f"Expires At: {result['expires_at']}")
        
    except PaymentServiceError as e:
        print(f"Error: {str(e)}") 