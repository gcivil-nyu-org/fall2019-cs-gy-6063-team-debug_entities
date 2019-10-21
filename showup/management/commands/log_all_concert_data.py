# This command puts all the concert data from our database into a log

from django.core.management.base import BaseCommand
from showup.models import Concert
import logging


class Command(BaseCommand):
    def handle(self, *args, **options):
        log_file = "showup/management/commands/logs/log_all_concert_data.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )  # setting up the logger to write to a file named log_all_concert_data.log

        for concert in Concert.objects.all():
            logging.debug(concert)
        logging.debug(
            "I printed all " + str(Concert.objects.count()) + " events in the database"
        )
