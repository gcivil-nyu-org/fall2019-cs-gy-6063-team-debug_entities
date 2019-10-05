# This command deletes all concert data. Use with caution.

from django.core.management.base import BaseCommand
from showup.models import Concert
import logging

class Command(BaseCommand):
    def handle(self, *args, **options):
        log_file = 'showup/management/commands/logs/delete_all_concert_data.log'
        logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') # setting up the logger to write to a file named delete_all_concert_data.log

        num_concerts = Concert.objects.count()
        Concert.objects.all().delete()
        logging.debug("I deleted all " + str(num_concerts) + " concerts from the database")