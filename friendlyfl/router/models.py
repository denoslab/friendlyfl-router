from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fsm import transition, FSMField


class Site(models.Model):
    """
    A site running local FL tasks
    """

    class SiteStatus(models.IntegerChoices):
        DISCONNECTED = 0
        CONNECTED = 1

    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField()
    uid = models.UUIDField(primary_key=False, unique=True)
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
            self.status = Site.SiteStatus.CONNECTED
        self.updated_at = curr_time
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
    tasks = models.JSONField(encoder=None, decoder=None, default='[]')
    batch = models.IntegerField()
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        curr_time = timezone.now()
        if not self.id:
            self.created_at = curr_time
            self.batch = 0
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
        return self.project.name + '-' + self.site.name

    class Meta:
        ordering = ['id']
        unique_together = ('site', 'project',)


class Run(models.Model):
    """
    Runs of a project.
    """

    class RunStatus(models.TextChoices):
        STANDBY = 'STANDBY'
        PREPARING = 'PREPARING'
        RUNNING = 'RUNNING'
        PENDING_SUCCESS = 'PENDING_SUCCESS'
        PENDING_FAILED = 'PENDING_FAILED'
        SUCCESS = 'SUCCESS'
        FAILED = 'FAILED'

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        ProjectParticipant, on_delete=models.CASCADE)
    batch = models.IntegerField()
    tasks = models.JSONField(encoder=None, decoder=None, default='[]')
    middle_artifacts = models.JSONField(
        encoder=None, decoder=None, default='[]')
    role = models.CharField(
        max_length=2,
        choices=ProjectParticipant.Role.choices,
        default=ProjectParticipant.Role.PARTICIPANT,
    )
    status = FSMField(
        choices=RunStatus.choices, default=RunStatus.STANDBY, protected=True)
    logs = models.JSONField(encoder=None, decoder=None, default='{}')
    artifacts = models.JSONField(encoder=None, decoder=None, default='{}')
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        curr_time = timezone.now()
        if not self.id:
            # copy the participant's role to the new record
            self.role = self.participant.role
            self.created_at = curr_time
            if ProjectParticipant.Role.COORDINATOR == self.role:
                self.project.batch += 1
                self.project.save()
            self.batch = self.project.batch
            self.tasks = self.project.tasks
            self.status = Run.RunStatus.STANDBY
        self.updated_at = curr_time
        return super(Run, self).save(*args, **kwargs)

    def __str__(self):
        return self.project.name + '-' + self.batch + '-' + self.id

    @staticmethod
    def update_status(instance, status):
        match status:
            case Run.RunStatus.PREPARING:
                instance.preparing()
            case Run.RunStatus.RUNNING:
                instance.running()
            case Run.RunStatus.PENDING_SUCCESS:
                instance.pending_success()
            case Run.RunStatus.PENDING_FAILED:
                instance.pending_failed()
            case Run.RunStatus.SUCCESS:
                instance.success()
            case Run.RunStatus.FAILED:
                instance.failed()
        return instance

    @transition(field=status, source=RunStatus.STANDBY, target=RunStatus.PREPARING)
    def preparing(self):
        print(self.status)

    @transition(field=status, source=RunStatus.PREPARING, target=RunStatus.RUNNING)
    def running(self):
        print(self.status)

    @transition(field=status, source=RunStatus.RUNNING, target=RunStatus.PENDING_SUCCESS)
    def pending_success(self):
        print(self.status)

    @transition(field=status, source=[RunStatus.RUNNING, RunStatus.PREPARING], target=RunStatus.PENDING_FAILED)
    def pending_failed(self):
        print(self.status)

    @transition(field=status, source=RunStatus.PENDING_SUCCESS, target=RunStatus.SUCCESS)
    def success(self):
        print(self.status)

    @transition(field=status, source=RunStatus.PENDING_FAILED, target=RunStatus.FAILED)
    def failed(self):
        print(self.status)

    class Meta:
        ordering = ['id']
        unique_together = ('project', 'participant', 'batch',)
