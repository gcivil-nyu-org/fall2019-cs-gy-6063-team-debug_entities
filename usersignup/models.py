from django.db import models

# Create your models here.
class UserSignup(models.Model):
    username = models.CharField(max_length=20)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    dateOfBirth = models.DateField()
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    password = models.CharField(max_length=30)
	
    def __str__(self):
        return self.username
		
class LoginUser(models.Model):
	username = models.CharField(max_length=20)
	password = models.CharField(max_length=30)
	isValidated = models.BooleanField()