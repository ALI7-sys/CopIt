from celery import Celery
from celery.schedules import crontab
from django.conf import settings

app = Celery('copit')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'process-orders-hourly': {
        'task': 'api.tasks.process_orders',
        'schedule': crontab(minute=0),  # Run at the start of every hour
        'options': {
            'expires': 3600  # Task expires after 1 hour
        }
    }
} 