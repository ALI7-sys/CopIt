import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from ...models import Order, OrderItem
from ...services.vcc_service import vcc_service
from ...services.fx import fx_service

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process paid orders and place them with US stores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually placing orders'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write('Running in dry-run mode')

        try:
            # Get paid orders from last hour
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            orders = Order.objects.filter(
                status='paid',
                created_at__gte=cutoff_time,
                vcc_created=False
            ).select_related('shipping_address')

            if not orders:
                self.stdout.write('No new paid orders found')
                return

            self.stdout.write(f'Processing {orders.count()} orders')

            for order in orders:
                try:
                    self.process_order(order, dry_run)
                except Exception as e:
                    logger.error(f"Failed to process order {order.id}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Order processing failed: {str(e)}")
            raise

    def process_order(self, order: Order, dry_run: bool):
        """Process a single order"""
        self.stdout.write(f'Processing order {order.id}')

        # 1. Create VCC for the order
        try:
            card = vcc_service.create_virtual_card(
                amount=order.total_amount,
                merchant=order.store_name.lower(),
                description=f"Order {order.id}"
            )
            
            if not dry_run:
                order.vcc_id = card['card_id']
                order.vcc_last4 = card['last4']
                order.vcc_expiry = card['expiry']
                order.vcc_created = True
                order.save()
            
            self.stdout.write(f'Created VCC for order {order.id}')
            
        except Exception as e:
            logger.error(f"VCC creation failed for order {order.id}: {str(e)}")
            raise

        # 2. Submit order to store
        try:
            if not dry_run:
                self.submit_to_store(order, card)
                order.status = 'processing'
                order.save()
            
            self.stdout.write(f'Submitted order {order.id} to store')
            
        except Exception as e:
            logger.error(f"Store submission failed for order {order.id}: {str(e)}")
            raise

        # 3. Send confirmation email
        try:
            if not dry_run:
                self.send_confirmation_email(order)
            
            self.stdout.write(f'Sent confirmation email for order {order.id}')
            
        except Exception as e:
            logger.error(f"Email sending failed for order {order.id}: {str(e)}")
            # Don't raise here, as the order is already placed

    def submit_to_store(self, order: Order, card: dict):
        """Submit order to the appropriate store"""
        store_api = self.get_store_api(order.store_name)
        
        # Prepare order data
        order_data = {
            'items': [
                {
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'price': str(item.price)
                }
                for item in order.items.all()
            ],
            'shipping_address': {
                'name': order.shipping_address.full_name,
                'street': order.shipping_address.street,
                'city': order.shipping_address.city,
                'state': order.shipping_address.state,
                'zip': order.shipping_address.zip_code,
                'country': order.shipping_address.country
            },
            'payment': {
                'card_number': f"**** **** **** {card['last4']}",
                'expiry': card['expiry'],
                'cvv': '***'
            }
        }
        
        # Submit to store
        response = store_api.create_order(order_data)
        
        # Update order with store reference
        order.store_order_id = response['order_id']
        order.save()

    def get_store_api(self, store_name: str):
        """Get appropriate store API client"""
        if store_name.lower() == 'newegg':
            from ...services.stores.newegg import NeweggAPI
            return NeweggAPI()
        elif store_name.lower() == 'backmarket':
            from ...services.stores.backmarket import BackMarketAPI
            return BackMarketAPI()
        else:
            raise ValueError(f"Unsupported store: {store_name}")

    def send_confirmation_email(self, order: Order):
        """Send order confirmation email to customer"""
        subject = f'Order Confirmation - Order #{order.id}'
        
        # Prepare email content
        items_list = '\n'.join([
            f"- {item.product_name} x {item.quantity} (${item.price})"
            for item in order.items.all()
        ])
        
        message = f"""
        Thank you for your order!

        Order Details:
        Order ID: {order.id}
        Total Amount: ${order.total_amount}
        
        Items:
        {items_list}
        
        Shipping Address:
        {order.shipping_address.full_name}
        {order.shipping_address.street}
        {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.zip_code}
        {order.shipping_address.country}
        
        We'll send you tracking information once your order ships.
        
        Best regards,
        CopIt Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False
        ) 