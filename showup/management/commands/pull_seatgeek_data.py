# This command pulls data from SeatGeek's API and adds concerts to
# our database if they're not already in there.

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
import json
import requests
import logging
from showup.models import Concert, Genre
from datetime import datetime


class Command(BaseCommand):
    def OpenGenre():
        genres_fromfile = set()
        file = "showup/static/Genres.txt"
        with open(file, "r") as existing_genre:
            lines = existing_genre.read().splitlines()
            for line in lines:
                genres_fromfile.add(line)
        return genres_fromfile

    def WriteGenre(genre_set):
        file = "showup/static/Genres.txt"
        with open(file, "w+") as genre_file:
            for genre in genre_set:
                genre_file.write(genre + "\n")

    def handle(self, *args, **options):
        base_url = (
            "https://api.seatgeek.com/2/events?client_id="
            "MTg3MzUxNzB8MTU3MDE1NTY1OS45MQ&per_page=5000&taxonomies.name=concert"
        )
        borough_urls = {
            "BK": "&lat=40.643222&lon=-73.949258&range=5mi",
            "QN": "&lat=40.720977&lon=-73.810735&range=6.5mi",
            "BX": "&lat=40.859827&lon=-73.862867&range=4mi",
            "SI": "&lat=40.573586&lon=-74.158318&range=5.8mi",
            "MN": "&lat=40.779527&lon=-73.966263&range=6mi",
        }
        # it's important that Manhattan is last because it's very badly
        # represented by a circle. So we do the other boroughs first so that the
        # inevitable overlap from MN's circle won't misassign concerts to MN.
        log_file = log_file = "showup/management/commands/logs/pull_seatgeek_data.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )  # setting up the logger to write to a file name pull_seatgeek_data.log

        existing_genres = Command.OpenGenre()

        for borough_abbrev in borough_urls:
            response = requests.get(base_url + borough_urls[borough_abbrev])
            concert_list = json.loads(response.content)[
                "events"
            ]  # each item in concert_list is a dict that represents an event.

            for concert in concert_list:
                if Concert.objects.filter(id=concert["id"]).exists():
                    logging.debug(
                        "I already have a concert with an id of " + str(concert["id"])
                    )
                else:
                    perf_name_list = [p["name"] for p in concert["performers"]]
                    # each concert has a list of performers so we
                    # add the name of each performer to this list

                    genres_set = set()
                    for perf in concert["performers"]:
                        # each concert has a list of performers and each performer has
                        # a list of genres. So we add all genres from all performers to
                        # genres_set. We use a set because there's
                        # no reason to have duplicated genres.
                        if "genres" in perf:
                            for g in perf["genres"]:
                                genres_set.add(g["name"])
                                existing_genres.add(g["name"])

                    aware_date = make_aware(
                        datetime.strptime(
                            concert["datetime_local"], "%Y-%m-%dT%H:%M:%S"
                        )
                    )
                    # We need to make the time given by the API into a timezone-aware
                    # time, because Django will complain otherwise

                    curr_concert = Concert(
                        id=concert["id"],
                        datetime=aware_date,
                        venue_name=concert["venue"]["name_v2"],
                        borough=borough_abbrev,
                        performer_names=", ".join(perf_name_list),
                        genres=", ".join(genres_set),
                        event_url=concert["url"],
                        performer_image_url=concert["performers"][0]["image"],
                    )
                    # parse all necessary information from the concert data and put
                    # it into an object in our database
                    logging.debug(
                        "I'm about to try to save this concert: Venue - "
                        + concert["venue"]["name_v2"]
                        + ", Performers - "
                        + ", ".join(perf_name_list)
                    )
                    curr_concert.save()
                    logging.debug(
                        "I just saved event " + str(concert["id"]) + " to the database"
                    )

        existing_genres = sorted(existing_genres)
        curr_genre = Genre(genre = ",".join(existing_genres))
        curr_genre.save()
        Command.WriteGenre(existing_genres)
