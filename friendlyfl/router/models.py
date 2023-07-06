from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
import uuid


class Site(models.Model):
    """
    A site running local FL tasks
    """
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    uid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('auth.User', default='admin', related_name='owner', on_delete=models.CASCADE)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Site, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_at']


class Project(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    tasks = models.JSONField(encoder=None, decoder=None)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
