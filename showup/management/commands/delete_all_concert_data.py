# This command deletes all concert data. Use with caution.

from django.core.management.base import BaseCommand
from showup.models import Concert

class Command(BaseCommand):
    def handle(self, *args, **options):
        Concert.objects.all().delete()
        print("Deleted all concerts")