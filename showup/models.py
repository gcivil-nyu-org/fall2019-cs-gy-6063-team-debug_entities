from django.db import models

class Concert(models.Model):
    BOROUGH_CHOICES = [
        ('BK', 'Brooklyn'),
        ('MN', 'Manhattan'),
        ('BX', 'The Bronx'),
        ('QN', 'Queens'),
        ('SI', 'Staten Island')
    ]

    id = models.IntegerField(primary_key = True)
    datetime = models.DateTimeField()
    venue_name = models.TextField()
    borough = models.TextField(choices = BOROUGH_CHOICES)
    performer_names = models.TextField()
    genres = models.TextField()
    event_url = models.URLField(max_length=100000)
    performer_image_url = models.URLField(max_length=100000, null = True)

    def __str__(self):
        return self.performer_names + " at " + self.venue_name + " on " + str(self.datetime) + " in " + self.borough


class Users(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    dateOfBirth = models.DateField()
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    is_verified = False
    logged_in = False

    def __str__(self):
        return self.email
