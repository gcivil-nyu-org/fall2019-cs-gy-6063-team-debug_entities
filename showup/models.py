from django.db import models

class Concert(models.Model):
    datetime = models.DateTimeField()
    venue_name = models.CharField(max_length = 100)
    performer_names = models.CharField(max_length = 200)
    event_url = models.URLField()
    performer_image_url = models.URLField()

    def __str__(self):
        return performer_names + " at " + venue_name + " on " + datetime