# This command prints all the concert data from our database

from django.core.management.base import BaseCommand
from showup.models import Concert

class Command(BaseCommand):
    def handle(self, *args, **options):        
        for concert in Concert.objects.all():
            print(concert)
        print("I printed all " + str(Concert.objects.count()) + " events in the database")