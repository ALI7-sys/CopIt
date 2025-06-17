from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from decimal import Decimal

class RevolutServiceError(Exception):
    """Base exception for Revolut service errors"""
    pass

class InvalidAPIVersionError(RevolutServiceError):
    """Raised when an invalid API version is used"""
    pass

class CardNotFoundError(RevolutServiceError):
    """Raised when a card is not found"""
    pass

class MerchantLockError(RevolutServiceError):
    """Raised when merchant locking fails"""
    pass

class APIResponse:
    """Standardized API response format"""
    def __init__(self, data: Dict, headers: Dict, status_code: int):
        self.data = data
        self.headers = headers
        self.status_code = status_code

class RevolutService:
    API_VERSION = '2024-09-01'
    BASE_URL = 'https://api.revolut.com/business/v1'
    CARD_EXPIRY_HOURS = 24
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.default_headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Revolut-Api-Version': self.API_VERSION
        }

    def _validate_api_version(self, headers: Dict) -> None:
        """Validate the API version in the request headers"""
        version = headers.get('Revolut-Api-Version')
        if not version:
            raise InvalidAPIVersionError('API version header is required')
        if version != self.API_VERSION:
            raise InvalidAPIVersionError(f'Invalid API version. Expected {self.API_VERSION}, got {version}')

    def _handle_response(self, response: requests.Response) -> APIResponse:
        """Handle API response and raise appropriate errors"""
        if response.status_code == 400:
            error_data = response.json()
            if 'Invalid API version' in error_data.get('message', ''):
                raise InvalidAPIVersionError(error_data['message'])
            raise RevolutServiceError(error_data.get('message', 'Bad request'))
        elif response.status_code == 404:
            raise CardNotFoundError('Card not found')
        elif response.status_code >= 500:
            raise RevolutServiceError('Internal server error')
        
        return APIResponse(
            data=response.json(),
            headers=dict(response.headers),
            status_code=response.status_code
        )

    def create_virtual_card(self, merchant_id: str, spend_limit: Optional[int] = None) -> Dict:
        """Create a new virtual card with merchant locking and expiry"""
        try:
            # Calculate expiry time (24 hours from now)
            expiry_time = (datetime.utcnow() + timedelta(hours=self.CARD_EXPIRY_HOURS)).isoformat()

            response = requests.post(
                f'{self.BASE_URL}/cards',
                headers=self.default_headers,
                json={
                    'type': 'VIRTUAL',
                    'spend_limit': spend_limit,
                    'expiry_time': expiry_time,
                    'merchant_id': merchant_id,
                    'merchant_locked': True
                }
            )
            result = self._handle_response(response)
            return result.data
        except requests.RequestException as e:
            raise RevolutServiceError(f'Failed to create virtual card: {str(e)}')

    def get_card(self, card_id: str) -> Dict:
        """Get card details"""
        try:
            response = requests.get(
                f'{self.BASE_URL}/cards/{card_id}',
                headers=self.default_headers
            )
            result = self._handle_response(response)
            return result.data
        except requests.RequestException as e:
            raise RevolutServiceError(f'Failed to get card: {str(e)}')

    def process_transaction(self, card_id: str, amount: int, merchant: str, description: str) -> Dict:
        """Process a transaction with the card"""
        try:
            # First verify the card exists and is not expired
            card = self.get_card(card_id)
            expiry_time = datetime.fromisoformat(card['expiry_time'].replace('Z', '+00:00'))
            
            if datetime.utcnow() > expiry_time:
                raise RevolutServiceError('Card has expired')

            # Process the transaction
            response = requests.post(
                f'{self.BASE_URL}/transactions',
                headers=self.default_headers,
                json={
                    'card_id': card_id,
                    'amount': amount,
                    'merchant': merchant,
                    'description': description
                }
            )
            result = self._handle_response(response)
            return result.data
        except CardNotFoundError:
            raise
        except requests.RequestException as e:
            raise RevolutServiceError(f'Failed to process transaction: {str(e)}')

    def get_transactions(self, card_id: Optional[str] = None, page: int = 1, limit: int = 10) -> Dict:
        """Get transaction history with pagination"""
        try:
            params = {
                'page': page,
                'limit': limit
            }
            if card_id:
                params['card_id'] = card_id

            response = requests.get(
                f'{self.BASE_URL}/transactions',
                headers=self.default_headers,
                params=params
            )
            result = self._handle_response(response)
            return result.data
        except requests.RequestException as e:
            raise RevolutServiceError(f'Failed to get transactions: {str(e)}')

# Create a singleton instance
revolut_service = RevolutService(api_key='test-api-key')  # Replace with actual API key from environment 