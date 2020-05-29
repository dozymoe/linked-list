import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linked_list.settings')

app = Celery('linked_list')
app.config_from_object('django.conf.settings', namespace='CELERY')
app.autodiscover_tasks()
