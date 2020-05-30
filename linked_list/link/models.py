from django.conf import settings
from django.db import models
from author.models import Author
from publisher.models import Publisher

class LinkKeyword(models.Model):
    name = models.CharField(max_length=32, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self): # pylint:disable=invalid-str-returned
        return self.name


class Link(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    text = models.TextField(null=True)
    html = models.TextField(null=True)

    notes = models.TextField(null=True)

    image = models.ImageField(blank=True, null=True)
    image_height = models.SmallIntegerField(null=True)
    image_width = models.SmallIntegerField(null=True)
    image_alt = models.TextField(null=True)

    author = models.ForeignKey(Author, null=True, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, null=True,
            on_delete=models.CASCADE)
    keywords = models.ManyToManyField(LinkKeyword)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True,
            on_delete=models.CASCADE)
    published_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
            db_index=True)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self): # pylint:disable=invalid-str-returned
        return self.title
