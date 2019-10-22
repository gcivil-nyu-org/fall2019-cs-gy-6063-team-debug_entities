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


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    interested = models.ManyToManyField(Concert, related_name="interested")
    going = models.ManyToManyField(Concert, related_name="going")
    bio = models.TextField(max_length=500, default="")

    def __str__(self):
        return self.email
