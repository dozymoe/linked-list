from django.conf import settings
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=70, db_index=True)

    image = models.ImageField(blank=True, null=True)
    image_height = models.SmallIntegerField(null=True)
    image_width = models.SmallIntegerField(null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True,
            on_delete=models.CASCADE)
    updated_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['name']

    def __str__(self): # pylint:disable=invalid-str-returned
        return self.name


class AuthorSocial(models.Model):
    url = models.URLField(db_index=True)
    entity = models.ForeignKey(Author, db_index=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True,
            on_delete=models.CASCADE)

    class Meta:
        ordering = ['url']

    def __str__(self): # pylint:disable=invalid-str-returned
        return self.url
