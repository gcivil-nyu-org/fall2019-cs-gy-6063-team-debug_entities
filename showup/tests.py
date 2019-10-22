from django.test import TestCase
from .models import Concert, CustomUser
import datetime


class ConcertModelTests(TestCase):
    def test_concert_string_contains_correct_info(self):
        test_concert = Concert(
            performer_names="Team Debug Entities",
            venue_name="Rogers Hall",
            datetime=datetime.date(2019, 1, 1),
            borough="BK",
        )

        desired_output = "Team Debug Entities at Rogers Hall on 2019-01-01 in BK"

        self.assertEqual(test_concert.__str__(), desired_output)


class CustomUserModelTests(TestCase):
    def test_customuser_string_contains_correct_info(self):
        test_customuser = CustomUser(
            first_name="Jerry", last_name="Seinfeld", email="jerry@seinfeld.com"
        )

        self.assertEqual(test_customuser.__str__(), "jerry@seinfeld.com")
