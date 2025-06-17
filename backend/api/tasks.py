from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_orders():
    """Process paid orders and place them with US stores"""
    try:
        logger.info("Starting order processing task")
        call_command('place_orders')
        logger.info("Order processing task completed successfully")
    except Exception as e:
        logger.error(f"Order processing task failed: {str(e)}")
        raise 