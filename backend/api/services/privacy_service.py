from typing import Dict, List, Optional
from datetime import datetime
import requests
from decimal import Decimal

class PrivacyServiceError(Exception):
    """Base exception for Privacy.com service errors"""
    pass

class InvalidAPIVersionError(PrivacyServiceError):
    """Raised when an invalid API version is used"""
    pass

class CardNotFoundError(PrivacyServiceError):
    """Raised when a card is not found"""
    pass

class APIResponse:
    """Standardized API response format"""
    def __init__(self, data: Dict, headers: Dict, status_code: int):
        self.data = data
        self.headers = headers
        self.status_code = status_code

class PrivacyService:
    API_VERSION = '2024-09-01'
    BASE_URL = 'https://api.privacy.com/v1'
    
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
            raise PrivacyServiceError(error_data.get('message', 'Bad request'))
        elif response.status_code == 404:
            raise CardNotFoundError('Card not found')
        elif response.status_code >= 500:
            raise PrivacyServiceError('Internal server error')
        
        return APIResponse(
            data=response.json(),
            headers=dict(response.headers),
            status_code=response.status_code
        )

    def create_card(self, type: str = 'VIRTUAL', spend_limit: Optional[int] = None) -> Dict:
        """Create a new virtual card"""
        try:
            response = requests.post(
                f'{self.BASE_URL}/cards',
                headers=self.default_headers,
                json={
                    'type': type,
                    'spend_limit': spend_limit
                }
            )
            result = self._handle_response(response)
            return result.data
        except requests.RequestException as e:
            raise PrivacyServiceError(f'Failed to create card: {str(e)}')

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
            raise PrivacyServiceError(f'Failed to get card: {str(e)}')

    def process_transaction(self, card_id: str, amount: int, merchant: str, description: str) -> Dict:
        """Process a transaction with the card"""
        try:
            # First verify the card exists
            self.get_card(card_id)

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
            raise PrivacyServiceError(f'Failed to process transaction: {str(e)}')

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
            raise PrivacyServiceError(f'Failed to get transactions: {str(e)}')

# Create a singleton instance
privacy_service = PrivacyService(api_key='test-api-key')  # Replace with actual API key from environment 