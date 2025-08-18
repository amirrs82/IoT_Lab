import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.timezone = 'UTC'

# Configure periodic tasks
app.conf.beat_schedule = {
    'update_currency_prices_every_5_minutes': {
        'task': 'cryptocurrency.tasks.update_currency_prices',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
