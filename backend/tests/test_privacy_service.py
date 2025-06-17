import pytest
from api.services.privacy_service import (
    privacy_service,
    PrivacyServiceError,
    InvalidAPIVersionError,
    CardNotFoundError
)

def test_create_and_use_virtual_card():
    # Create a new virtual card
    card = privacy_service.create_virtual_card(
        spend_limit=1000,  # $10.00
        memo="Test card for CopIt"
    )
    assert card['type'] == 'virtual'
    assert card['state'] == 'active'
    assert card['spend_limit'] == 1000
    assert card['memo'] == "Test card for CopIt"

    # Get card details
    card_details = privacy_service.get_card_details(card['id'])
    assert card_details == card

    # Process a transaction
    transaction = privacy_service.process_transaction(
        card_id=card['id'],
        amount=500,  # $5.00
        merchant="CopIt Store",
        description="Test purchase"
    )
    assert transaction['card_id'] == card['id']
    assert transaction['amount'] == 500
    assert transaction['merchant'] == "CopIt Store"
    assert transaction['description'] == "Test purchase"
    assert transaction['status'] in ['approved', 'declined']

    # Get transaction history
    transactions = privacy_service.get_transactions(card_id=card['id'])
    assert len(transactions['data']) > 0
    assert transactions['data'][0]['id'] == transaction['id']

    # Update card
    updated_card = privacy_service.update_card(
        card_id=card['id'],
        spend_limit=2000  # $20.00
    )
    assert updated_card['spend_limit'] == 2000

    # Terminate card
    terminated_card = privacy_service.terminate_card(card['id'])
    assert terminated_card['state'] == 'terminated'

def test_list_cards():
    # Create multiple cards
    card1 = privacy_service.create_virtual_card(memo="Card 1")
    card2 = privacy_service.create_virtual_card(memo="Card 2")
    card3 = privacy_service.create_virtual_card(memo="Card 3")

    # List all cards
    all_cards = privacy_service.list_cards()
    assert len(all_cards['data']) >= 3

    # List active cards
    active_cards = privacy_service.list_cards(state='active')
    assert all(card['state'] == 'active' for card in active_cards['data'])

    # List virtual cards
    virtual_cards = privacy_service.list_cards(type='virtual')
    assert all(card['type'] == 'virtual' for card in virtual_cards['data'])

def test_transaction_pagination():
    # Create a card
    card = privacy_service.create_virtual_card()

    # Create multiple transactions
    for i in range(25):
        privacy_service.process_transaction(
            card_id=card['id'],
            amount=100,
            merchant=f"Store {i}",
            description=f"Transaction {i}"
        )

    # Test pagination
    page1 = privacy_service.get_transactions(card_id=card['id'], page=1, page_size=10)
    page2 = privacy_service.get_transactions(card_id=card['id'], page=2, page_size=10)
    page3 = privacy_service.get_transactions(card_id=card['id'], page=3, page_size=10)

    assert len(page1['data']) == 10
    assert len(page2['data']) == 10
    assert len(page3['data']) == 5
    assert page1['total_entries'] == 25
    assert page1['total_pages'] == 3

def test_error_handling():
    # Test with non-existent card
    with pytest.raises(CardNotFoundError):
        privacy_service.get_card_details("non-existent-id")

    with pytest.raises(CardNotFoundError):
        privacy_service.process_transaction(
            card_id="non-existent-id",
            amount=100,
            merchant="Test Store"
        )

    with pytest.raises(CardNotFoundError):
        privacy_service.update_card(
            card_id="non-existent-id",
            spend_limit=1000
        )

    with pytest.raises(CardNotFoundError):
        privacy_service.terminate_card("non-existent-id")

def test_api_version_handling():
    # Create a card with default version
    card = privacy_service.create_virtual_card()
    assert card['type'] == 'virtual'

    # Test with invalid API version
    privacy_service.api._api_version = '2024-08-01'  # Temporarily change version
    with pytest.raises(InvalidAPIVersionError):
        privacy_service.create_virtual_card()
    
    # Restore correct version
    privacy_service.api._api_version = '2024-09-01'
    card = privacy_service.create_virtual_card()
    assert card['type'] == 'virtual' 