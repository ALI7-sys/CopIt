import logging
from typing import Dict, Optional, List
from decimal import Decimal
import requests
from datetime import datetime, timedelta
from django.conf import settings
from .fx import fx_service

logger = logging.getLogger(__name__)

class VCCServiceError(Exception):
    """Base exception for VCC service errors"""
    pass

class InsufficientBalanceError(VCCServiceError):
    """Raised when there are insufficient funds for card creation"""
    pass

class CardCreationError(VCCServiceError):
    """Raised when card creation fails"""
    pass

class CardNotFoundError(VCCServiceError):
    """Raised when card is not found"""
    pass

class VCCService:
    """Service for managing virtual credit cards with Revolut"""
    
    BASE_URL = 'https://api.revolut.com/v1'
    SUPPORTED_MERCHANTS = {
        'newegg': {
            'name': 'Newegg',
            'merchant_id': 'newegg_merchant_id',  # Replace with actual merchant ID
            'category': 'electronics'
        },
        'backmarket': {
            'name': 'Back Market',
            'merchant_id': 'backmarket_merchant_id',  # Replace with actual merchant ID
            'category': 'electronics'
        }
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.default_headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and raise appropriate errors"""
        if response.status_code == 401:
            raise VCCServiceError('Invalid API credentials')
        elif response.status_code == 403:
            raise VCCServiceError('Insufficient permissions')
        elif response.status_code >= 500:
            raise VCCServiceError('Revolut API error')
        
        try:
            return response.json()
        except ValueError:
            raise VCCServiceError('Invalid response from Revolut API')

    def _validate_merchant(self, merchant: str) -> Dict:
        """Validate and return merchant details"""
        merchant = merchant.lower()
        if merchant not in self.SUPPORTED_MERCHANTS:
            raise VCCServiceError(f'Unsupported merchant: {merchant}')
        return self.SUPPORTED_MERCHANTS[merchant]

    def create_virtual_card(
        self,
        amount: Decimal,
        merchant: str,
        description: Optional[str] = None
    ) -> Dict:
        """
        Create a virtual credit card with merchant restrictions
        
        Args:
            amount: Maximum card limit in USD
            merchant: Target merchant (newegg or backmarket)
            description: Optional card description
        
        Returns:
            Dict: Card details including ID, last 4 digits, and expiry
        
        Raises:
            VCCServiceError: If card creation fails
            InsufficientBalanceError: If insufficient USD balance
        """
        try:
            # Validate merchant
            merchant_details = self._validate_merchant(merchant)
            
            # Check Payoneer USD balance
            usd_balance = fx_service.get_usd_balance()
            if amount > usd_balance:
                raise InsufficientBalanceError(
                    f"Insufficient USD balance. Required: {amount}, Available: {usd_balance}"
                )
            
            # Calculate expiry (24 hours from now)
            expiry = datetime.utcnow() + timedelta(hours=24)
            
            # Create virtual card
            response = requests.post(
                f'{self.BASE_URL}/cards',
                headers=self.default_headers,
                json={
                    'type': 'virtual',
                    'currency': 'USD',
                    'limit': str(amount),
                    'expiry_date': expiry.isoformat(),
                    'merchant_restrictions': {
                        'merchant_id': merchant_details['merchant_id'],
                        'category': merchant_details['category']
                    },
                    'description': description or f"VCC for {merchant_details['name']}"
                }
            )
            
            data = self._handle_response(response)
            
            # Log card creation
            logger.info(
                f"Virtual card created - ID: {data['id']}, "
                f"Merchant: {merchant_details['name']}, "
                f"Limit: {amount} USD, "
                f"Expiry: {expiry}"
            )
            
            return {
                'card_id': data['id'],
                'last4': data['last4'],
                'expiry': expiry.isoformat(),
                'merchant': merchant_details['name'],
                'limit': amount
            }
            
        except InsufficientBalanceError:
            raise
        except Exception as e:
            raise CardCreationError(f"Failed to create virtual card: {str(e)}")

    def get_card_details(self, card_id: str) -> Dict:
        """
        Get details for a specific virtual card
        
        Args:
            card_id: ID of the virtual card
        
        Returns:
            Dict: Card details including status and transactions
        
        Raises:
            VCCServiceError: If card details retrieval fails
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/cards/{card_id}',
                headers=self.default_headers
            )
            
            data = self._handle_response(response)
            
            return {
                'card_id': data['id'],
                'last4': data['last4'],
                'expiry': data['expiry_date'],
                'status': data['status'],
                'limit': Decimal(str(data['limit'])),
                'available_balance': Decimal(str(data['available_balance'])),
                'merchant_restrictions': data['merchant_restrictions']
            }
            
        except Exception as e:
            raise VCCServiceError(f"Failed to get card details: {str(e)}")

    def list_active_cards(self) -> List[Dict]:
        """
        List all active virtual cards
        
        Returns:
            List[Dict]: List of active card details
        
        Raises:
            VCCServiceError: If card listing fails
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/cards',
                headers=self.default_headers,
                params={'status': 'active'}
            )
            
            data = self._handle_response(response)
            
            return [{
                'card_id': card['id'],
                'last4': card['last4'],
                'expiry': card['expiry_date'],
                'merchant': card['merchant_restrictions']['merchant_id'],
                'limit': Decimal(str(card['limit'])),
                'available_balance': Decimal(str(card['available_balance']))
            } for card in data['cards']]
            
        except Exception as e:
            raise VCCServiceError(f"Failed to list active cards: {str(e)}")

    def cancel_card(self, card_id: str) -> Dict:
        """
        Cancel a virtual card
        
        Args:
            card_id: ID of the virtual card to cancel
        
        Returns:
            Dict: Cancellation details
        
        Raises:
            VCCServiceError: If cancellation fails
            CardNotFoundError: If card doesn't exist
        """
        try:
            response = requests.post(
                f'{self.BASE_URL}/cards/{card_id}/cancel',
                headers=self.default_headers
            )
            
            if response.status_code == 404:
                raise CardNotFoundError(f"Card not found: {card_id}")
            
            data = self._handle_response(response)
            
            logger.info(f"Card cancelled - ID: {card_id}")
            
            return {
                'card_id': card_id,
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow().isoformat()
            }
            
        except CardNotFoundError:
            raise
        except Exception as e:
            raise VCCServiceError(f"Failed to cancel card: {str(e)}")

    def get_card_transactions(
        self,
        card_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get transactions for a specific card
        
        Args:
            card_id: ID of the virtual card
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
        
        Returns:
            List[Dict]: List of transaction details
        
        Raises:
            VCCServiceError: If transaction retrieval fails
            CardNotFoundError: If card doesn't exist
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date.isoformat()
            if end_date:
                params['end_date'] = end_date.isoformat()
            
            response = requests.get(
                f'{self.BASE_URL}/cards/{card_id}/transactions',
                headers=self.default_headers,
                params=params
            )
            
            if response.status_code == 404:
                raise CardNotFoundError(f"Card not found: {card_id}")
            
            data = self._handle_response(response)
            
            return [{
                'transaction_id': tx['id'],
                'amount': Decimal(str(tx['amount'])),
                'currency': tx['currency'],
                'status': tx['status'],
                'merchant': tx['merchant'],
                'timestamp': tx['created_at'],
                'description': tx.get('description', '')
            } for tx in data['transactions']]
            
        except CardNotFoundError:
            raise
        except Exception as e:
            raise VCCServiceError(f"Failed to get card transactions: {str(e)}")

    def get_card_usage_stats(self, card_id: str) -> Dict:
        """
        Get usage statistics for a specific card
        
        Args:
            card_id: ID of the virtual card
        
        Returns:
            Dict: Usage statistics including total spent, transaction count, etc.
        
        Raises:
            VCCServiceError: If stats retrieval fails
            CardNotFoundError: If card doesn't exist
        """
        try:
            # Get card details
            card_details = self.get_card_details(card_id)
            
            # Get all transactions
            transactions = self.get_card_transactions(card_id)
            
            # Calculate statistics
            total_spent = sum(tx['amount'] for tx in transactions)
            successful_tx = [tx for tx in transactions if tx['status'] == 'completed']
            failed_tx = [tx for tx in transactions if tx['status'] == 'failed']
            
            return {
                'card_id': card_id,
                'total_spent': total_spent,
                'available_balance': card_details['available_balance'],
                'transaction_count': len(transactions),
                'successful_transactions': len(successful_tx),
                'failed_transactions': len(failed_tx),
                'last_transaction': transactions[0] if transactions else None,
                'created_at': card_details.get('created_at'),
                'expiry': card_details['expiry']
            }
            
        except CardNotFoundError:
            raise
        except Exception as e:
            raise VCCServiceError(f"Failed to get card usage stats: {str(e)}")

# Create a singleton instance
vcc_service = VCCService(api_key=settings.REVOLUT_API_KEY) 