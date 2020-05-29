from django.conf import settings
from django.db import models

class FormData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True,
            on_delete=models.CASCADE)
    data = models.TextField()

    accessed_at = models.DateTimeField(auto_now_add=True, editable=False)
