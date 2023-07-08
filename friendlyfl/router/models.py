from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
import uuid
from django.utils.translation import gettext_lazy as _


class Site(models.Model):
    """
    A site running local FL tasks
    """

    class SiteStatus(models.IntegerChoices):
        DISCONNECTED = 0
        CONNECTED = 1

    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    uid = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        'auth.User', default='admin', related_name='owner', on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=SiteStatus.choices, default=SiteStatus.DISCONNECTED)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        curr_time = timezone.now()
        if not self.id:
            self.created_at = curr_time
        self.updated_at = curr_time
        self.status = Site.SiteStatus.CONNECTED
        return super(Site, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class Project(models.Model):
    """
        A project for a group of FL tasks defined.
    """
    name = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    tasks = models.JSONField(encoder=None, decoder=None)
    batch = models.IntegerField()
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        curr_time = timezone.now()
        if not self.id:
            self.created_at = curr_time
            self.batch = 1
        self.updated_at = curr_time
        return super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class ProjectParticipant(models.Model):
    """
    Participants of a project and their roles.
    """

    class Role(models.TextChoices):
        COORDINATOR = "CO", _("coordinator")
        PARTICIPANT = "PA", _("participant")

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.PARTICIPANT,
    )
    notes = models.TextField()
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        curr_time = timezone.now()
        if not self.id:
            self.created_at = curr_time
        self.updated_at = curr_time
        return super(ProjectParticipant, self).save(*args, **kwargs)

    def __str__(self):
        return self.project + '-' + site.name

    class Meta:
        ordering = ['id']
        unique_together = ('site', 'project',)


class Run(models.Model):
    """
    Runs of a project.
    """

    class RunStatus(models.IntegerChoices):
        STANDBY = 0
        PREPARING = 1
        RUNNING = 2
        PENDING_SUCCESS = 3
        PENDING_FAILED = 4
        SUCCESS = 5
        FAILED = 6

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        ProjectParticipant, on_delete=models.CASCADE)
    batch = models.IntegerField()
    role = models.CharField(
        max_length=2,
        choices=ProjectParticipant.Role.choices,
        default=ProjectParticipant.Role.PARTICIPANT,
    )
    status = models.IntegerField(
        choices=RunStatus.choices, default=RunStatus.STANDBY)
    logs = models.TextField()
    artifacts = models.JSONField(encoder=None, decoder=None, default='{}')
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        curr_time = timezone.now()
        if not self.id:
            # copy the participant's role to the new record
            self.role = self.participant.role
            self.batch = self.project.batch
            self.created_at = curr_time
            if ProjectParticipant.Role.COORDINATOR == role:
                # TODO: need to increase project batch
                pass
        self.updated_at = curr_time
        return super(Run, self).save(*args, **kwargs)

    def __str__(self):
        return self.project + '-' + self.id

    class Meta:
        ordering = ['id']
        unique_together = ('project', 'participant', 'batch',)
