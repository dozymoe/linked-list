from django.contrib import admin

from . import models

admin.site.register(models.Link)
admin.site.register(models.LinkKeyword)
