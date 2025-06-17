import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import random
from dataclasses import dataclass

@dataclass
class APIResponse:
    data: Dict
    headers: Dict[str, str]
    status_code: int = 200

class MockPrivacyAPI:
    def __init__(self):
        self.cards: Dict[str, Dict] = {}
        self.transactions: List[Dict] = []
        self._mock_card_types = ['virtual', 'physical']
        self._mock_card_networks = ['visa', 'mastercard']
        self._mock_card_states = ['active', 'suspended', 'terminated']
        self._mock_transaction_states = ['approved', 'declined', 'pending']
        self._api_version = '2024-09-01'

    def _create_response(self, data: Dict) -> APIResponse:
        """Create a standardized API response with headers"""
        return APIResponse(
            data=data,
            headers={
                'Revolut-Api-Version': self._api_version,
                'Content-Type': 'application/json'
            }
        )

    def create_card(self, 
                   type: str = 'virtual',
                   spend_limit: Optional[int] = None,
                   state: str = 'active',
                   funding_token: Optional[str] = None,
                   headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Mock card creation endpoint"""
        if headers and headers.get('Revolut-Api-Version') != self._api_version:
            return APIResponse(
                data={'error': 'Invalid API version'},
                headers={'Content-Type': 'application/json'},
                status_code=400
            )

        card_id = str(uuid.uuid4())
        card = {
            'id': card_id,
            'type': type,
            'spend_limit': spend_limit,
            'state': state,
            'funding_token': funding_token,
            'created_at': datetime.utcnow().isoformat(),
            'last_four': str(random.randint(1000, 9999)),
            'card_number': f"4111-1111-1111-{random.randint(1000, 9999)}",
            'exp_month': random.randint(1, 12),
            'exp_year': datetime.now().year + random.randint(1, 5),
            'cvv': str(random.randint(100, 999)),
            'network': random.choice(self._mock_card_networks),
            'hostname': 'mock-privacy.com',
            'memo': f"Mock card for testing - {card_id[:8]}"
        }
        self.cards[card_id] = card
        return self._create_response(card)

    def get_card(self, card_id: str, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Mock get card details endpoint"""
        if headers and headers.get('Revolut-Api-Version') != self._api_version:
            return APIResponse(
                data={'error': 'Invalid API version'},
                headers={'Content-Type': 'application/json'},
                status_code=400
            )

        card = self.cards.get(card_id)
        if not card:
            return APIResponse(
                data={'error': f'Card {card_id} not found'},
                headers={'Content-Type': 'application/json'},
                status_code=404
            )
        return self._create_response(card)

    def list_cards(self, 
                  page: int = 1,
                  page_size: int = 20,
                  type: Optional[str] = None,
                  state: Optional[str] = None,
                  headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Mock list cards endpoint"""
        if headers and headers.get('Revolut-Api-Version') != self._api_version:
            return APIResponse(
                data={'error': 'Invalid API version'},
                headers={'Content-Type': 'application/json'},
                status_code=400
            )

        filtered_cards = self.cards.values()
        
        if type:
            filtered_cards = [c for c in filtered_cards if c['type'] == type]
        if state:
            filtered_cards = [c for c in filtered_cards if c['state'] == state]

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_cards = list(filtered_cards)[start_idx:end_idx]

        response_data = {
            'data': paginated_cards,
            'page': page,
            'page_size': page_size,
            'total_entries': len(filtered_cards),
            'total_pages': (len(filtered_cards) + page_size - 1) // page_size
        }
        return self._create_response(response_data)

    def simulate_transaction(self,
                           card_id: str,
                           amount: int,
                           merchant: str,
                           description: Optional[str] = None,
                           headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Mock transaction simulation endpoint"""
        if headers and headers.get('Revolut-Api-Version') != self._api_version:
            return APIResponse(
                data={'error': 'Invalid API version'},
                headers={'Content-Type': 'application/json'},
                status_code=400
            )

        card = self.cards.get(card_id)
        if not card:
            return APIResponse(
                data={'error': f'Card {card_id} not found'},
                headers={'Content-Type': 'application/json'},
                status_code=404
            )

        # Simulate random transaction approval/decline
        is_approved = random.random() > 0.1  # 90% approval rate
        
        transaction = {
            'id': str(uuid.uuid4()),
            'card_id': card_id,
            'amount': amount,
            'merchant': merchant,
            'description': description or f"Mock transaction at {merchant}",
            'created_at': datetime.utcnow().isoformat(),
            'status': 'approved' if is_approved else 'declined',
            'decline_reason': None if is_approved else random.choice([
                'insufficient_funds',
                'card_suspended',
                'fraud_detected',
                'invalid_card'
            ])
        }
        
        self.transactions.append(transaction)
        return self._create_response(transaction)

    def list_transactions(self,
                         card_id: Optional[str] = None,
                         page: int = 1,
                         page_size: int = 20,
                         headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Mock list transactions endpoint"""
        if headers and headers.get('Revolut-Api-Version') != self._api_version:
            return APIResponse(
                data={'error': 'Invalid API version'},
                headers={'Content-Type': 'application/json'},
                status_code=400
            )

        filtered_transactions = self.transactions
        
        if card_id:
            filtered_transactions = [t for t in filtered_transactions if t['card_id'] == card_id]

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_transactions = list(filtered_transactions)[start_idx:end_idx]

        response_data = {
            'data': paginated_transactions,
            'page': page,
            'page_size': page_size,
            'total_entries': len(filtered_transactions),
            'total_pages': (len(filtered_transactions) + page_size - 1) // page_size
        }
        return self._create_response(response_data)

    def update_card(self,
                   card_id: str,
                   state: Optional[str] = None,
                   spend_limit: Optional[int] = None,
                   headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Mock update card endpoint"""
        if headers and headers.get('Revolut-Api-Version') != self._api_version:
            return APIResponse(
                data={'error': 'Invalid API version'},
                headers={'Content-Type': 'application/json'},
                status_code=400
            )

        card = self.cards.get(card_id)
        if not card:
            return APIResponse(
                data={'error': f'Card {card_id} not found'},
                headers={'Content-Type': 'application/json'},
                status_code=404
            )

        if state:
            card['state'] = state
        if spend_limit is not None:
            card['spend_limit'] = spend_limit

        return self._create_response(card)

    def terminate_card(self, card_id: str, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Mock terminate card endpoint"""
        if headers and headers.get('Revolut-Api-Version') != self._api_version:
            return APIResponse(
                data={'error': 'Invalid API version'},
                headers={'Content-Type': 'application/json'},
                status_code=400
            )

        card = self.cards.get(card_id)
        if not card:
            return APIResponse(
                data={'error': f'Card {card_id} not found'},
                headers={'Content-Type': 'application/json'},
                status_code=404
            )

        card['state'] = 'terminated'
        return self._create_response(card)

# Create a singleton instance
mock_privacy = MockPrivacyAPI() 