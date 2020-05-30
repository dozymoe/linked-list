import os
import time
from django.conf import settings
from celery import shared_task

@shared_task
def cleanup_formdata_uploads():
    now = time.time()
    for fname in os.listdir(settings.FORM_DATA_UPLOAD_DIR):
        f = os.path.join(settings.FORM_DATA_UPLOAD_DIR, fname)
        if not os.path.isfile(f):
            continue
        if os.path.getmtime(f) < now - (7 * 24 * 60 * 60):
            os.remove(f)
