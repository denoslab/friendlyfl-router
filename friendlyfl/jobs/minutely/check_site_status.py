from django.utils import timezone
from django_extensions.management.jobs import MinutelyJob

from friendlyfl.router.models import Site


class Job(MinutelyJob):
    help = "Site status checking job"

    def execute(self):
        now = timezone.now()
        sites = Site.objects.filter(status=Site.SiteStatus.CONNECTED)
        if not sites:
            return
        for site in sites:
            time_diff = now - site.updated_at
            if time_diff.seconds > 60:
                site.status = Site.SiteStatus.DISCONNECTED
                site.save()
