from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        s = Site.objects.get(id=1)
        s.domain = "showup-nyc.herokuapp.com"
        s.name = "showup-nyc.herokuapp.com"
        s.save()
