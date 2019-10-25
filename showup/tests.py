from .models import Concert, CustomUser
import datetime
from django.test import TestCase
from django.urls import reverse
from allauth.account.admin import EmailAddress


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


class AuthenticatedViewTests(TestCase):
    def setUp(self):  # this logs in a test user for the subsequent test cases
        username = "testuser"
        password = "testpass"
        testuser = CustomUser.objects.create_user(username=username, password=password)
        EmailAddress.objects.get_or_create(id=1, user=testuser, verified=True)
        self.client.login(username=username, password=password)

    def test_authed_user_can_see_events(self):
        self.response = self.client.get(reverse("events"))
        self.assertEqual(self.response.status_code, 200)
        # we want the status code to be 200 because that means
        # the request was successful

    def test_authed_user_can_see_user_profile(self):
        self.response = self.client.get(reverse("user", args=(1,)))
        self.assertEqual(self.response.status_code, 200)

    def test_authed_user_can_edit_profile(self):
        self.response = self.client.get(reverse("edit_profile", args=(1,)))
        self.assertEqual(self.response.status_code, 200)


class UnauthenticatedViewTests(TestCase):
    def test_unauthed_user_cannot_see_events(self):
        self.response = self.client.get(reverse("events"))
        self.assertEqual(self.response.status_code, 302)
        # we want the status code to be 302 because that means we were redirected

    def test_unauthed_user_cannot_see_user_profile(self):
        self.response = self.client.get(reverse("user", args=(1,)))
        self.assertEqual(self.response.status_code, 302)

    def test_unauthed_user_cannot_edit_profile(self):
        self.response = self.client.get(reverse("edit_profile", args=(1,)))
        self.assertEqual(self.response.status_code, 302)
