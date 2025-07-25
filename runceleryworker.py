import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CantinaShop.settings')

app = Celery('CantinaShop')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if __name__ == '__main__':
    # Start the worker with loglevel=info and pool=solo for Windows compatibility
    app.worker_main(['worker', '--loglevel=info', '--pool=solo'])
