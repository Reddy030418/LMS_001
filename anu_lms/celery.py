import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anu_lms.settings')

app = Celery('anu_lms')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule Configuration
app.conf.beat_schedule = {
    'send-daily-overdue-reminders': {
        'task': 'portal.tasks.send_due_reminders',
        # Executes every day at 8:00 AM
        'schedule': crontab(hour=8, minute=0),
    },
}
