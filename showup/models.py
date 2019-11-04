from django.db import models
from django.contrib.auth.models import AbstractUser


class Concert(models.Model):
    BOROUGH_CHOICES = [
        ("BK", "Brooklyn"),
        ("MN", "Manhattan"),
        ("BX", "The Bronx"),
        ("QN", "Queens"),
        ("SI", "Staten Island"),
    ]

    id = models.IntegerField(primary_key=True)
    datetime = models.DateTimeField()
    venue_name = models.TextField()
    borough = models.TextField(choices=BOROUGH_CHOICES)
    performer_names = models.TextField()
    genres = models.TextField()
    event_url = models.URLField(max_length=100000)
    performer_image_url = models.URLField(max_length=100000, null=True)

    def __str__(self):
        return "{} at {} on {} in {}".format(
            self.performer_names, self.venue_name, str(self.datetime), self.borough
        )


class Genre(models.Model):
    genre = models.TextField()

    def __str__(self):
        return self.genre


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=255, blank=True)
    interested = models.ManyToManyField(Concert, related_name="interested")
    going = models.ManyToManyField(Concert, related_name="going")
    bio = models.TextField(max_length=500, default="", blank=True)
    genres = models.ManyToManyField(Genre, related_name="genres")

    def __str__(self):
        return self.email


class Match(models.Model):
    """
    In order to avoid duplicate rows (i.e. [uid_1, uid_2] and [uid_2, uid_1]),
    the following constraints must hold:

    uid_1 != uid_2 && uid_1 < uid_2

    The default value of BooleanField is None when Field.default isn’t defined.
    """

    uid_1 = models.IntegerField()
    uid_2 = models.IntegerField()
    eid = models.IntegerField()
    decision_1 = models.NullBooleanField(default=None)  # uid_1 decision about uid_2.
    decision_2 = models.NullBooleanField(default=None)  # uid_2 decision about uid_1.
    decision = models.NullBooleanField(default=None)

    def __str__(self):
        return "{} {} {} {}".format(self.uid_1, self.uid_2, self.eid, self.decision)
