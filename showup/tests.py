import datetime

from .models import Concert, CustomUser, Genre, Swipe, Squad, SquadSwipe
from allauth.account.admin import EmailAddress
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import make_aware, utc


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


class GenreModelTests(TestCase):
    def test_genre_basic(self):
        genre = Genre(genre="EDM")
        genre.save()
        self.assertEqual(genre.__str__(), "EDM")


class CustomUserModelTests(TestCase):
    def test_customuser_basic(self):
        user = CustomUser(
            first_name="Jerry",
            last_name="Springer",
            date_of_birth="1944-02-13",
            gender="Man",
            email="jspringer@example.com",
        )
        user.save()
        self.assertEqual(user.__str__(), "jspringer@example.com")

    def test_customuser_form(self):
        # Create form data.
        data = {
            "first_name": "Jerry",
            "last_name": "Springer",
            "date_of_birth": "1944-02-13",
            "gender": "Man",
            "email": "jspringer@example.com",
            "password1": "heyhey123",
            "password2": "heyhey123",
        }

        # Send a POST request containing the form data.
        c = Client()
        c.post("/accounts/signup/", data)

        # Ensure the POST request was successful.
        user = CustomUser.objects.get(email="jspringer@example.com")
        self.assertEqual(user.last_name, "Springer")


class SwipeModelTests(TestCase):
    def test_swipe_basic(self):
        # Create needed objects for Swipe model.
        swiper = CustomUser(username="1", email="swiper@example.com")
        swipee = CustomUser(username="2", email="swipee@example.com")
        event = Concert(id=1, datetime=datetime.datetime.now(tz=utc))
        direction = True

        # Save the objects.
        swiper.save()
        swipee.save()
        event.save()

        # Create the Swipe object.
        swipe = Swipe(swiper=swiper, swipee=swipee, event=event, direction=direction)

        # Save the Swipe object.
        swipe.save()

        expected_output = (
            f"Swiper: {swiper.email}, "
            f"Swipee: {swipee.email}, "
            f"Event: {event.id}, "
            f"Direction: {direction}"
        )
        self.assertEqual(swipe.__str__(), expected_output)


class SquadModelTests(TestCase):
    def test_Squad_basic(self):
        squad = Squad()
        squad.save()
        self.assertEqual(squad.__str__(), str(squad.id))


class SquadSwipeModelTests(TestCase):
    def test_SquadSwipe_basic(self):
        # Create needed objects for Swipe model.
        swiper = Squad(id="1")
        swipee = Squad(id="2")
        direction = True

        # Save the objects.
        swiper.save()
        swipee.save()

        # Create the Swipe object.
        swipe = SquadSwipe(swiper=swiper, swipee=swipee, direction=direction)

        # Save the Swipe object.
        swipe.save()

        expected_output = (
            f"Swiper: {swiper.id}, " f"Swipee: {swipee.id}, " f"Direction: {direction}"
        )
        self.assertEqual(swipe.__str__(), expected_output)


class HomeViewTests(TestCase):
    def test_home_basic(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class EventsViewTests(TestCase):
    def setUp(self):
        # Create and save user.
        username, password = "jspringer@example.com", "heyhey123"
        user = CustomUser.objects.create_user(username=username, password=password)
        EmailAddress.objects.get_or_create(id=1, user=user, verified=True)

        # Login user.
        self.client.login(username=username, password=password)

        # Create and save event.
        event = Concert(id=1, datetime=datetime.datetime.now(tz=utc), borough="BK")
        event.save()

    def test_events_filter_borough(self):
        get = "?boroughs=BK&performers=&genres=&start_date=&end_date=&filter=#"
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)

    def test_events_filter_venue(self):
        get = (
            "?performers=&venues=American+Cheez&genres=&start_date=&end_date=&filter=#"
        )
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)

    def test_events_interested(self):
        get = "?interested=1"
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)

    def test_events_going(self):
        get = "?going=1"
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)

    def test_events_interested_going(self):
        get = "?going=1"
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)
        get = "?interested=1"
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)

    def test_events_going_not_going(self):
        get = "?going=1"
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)
        get = "?going=1"
        response = self.client.get(reverse("events") + get)
        self.assertEqual(response.status_code, 200)


class UserViewTests(TestCase):
    def setUp(self):
        # Create and save user.
        username, password = "jspringer@example.com", "heyhey123"
        user = CustomUser.objects.create_user(username=username, password=password)
        EmailAddress.objects.get_or_create(id=1, user=user, verified=True)

        # Login user.
        self.client.login(username=username, password=password)

    def test_user_unverified(self):
        # Create and save user.
        user = CustomUser(
            first_name="Jerry",
            last_name="Seinfeld",
            date_of_birth="1954-04-29",
            gender="Man",
            email="jseinfeld@example.com",
        )
        user.save()

        # Create and save email.
        email = EmailAddress(
            email="jseinfeld@example.com", user=user, primary=False, verified=False
        )
        email.save()

        # Try to view unverified user's profile.
        get = "2"
        response = self.client.get("/u/" + get)  # FIXME (use reverse())
        self.assertEqual(response.status_code, 403)


class EditProfileViewTests(TestCase):
    def setUp(self):
        # Create and save user.
        username, password = "jspringer@example.com", "heyhey123"
        user = CustomUser.objects.create_user(username=username, password=password)
        EmailAddress.objects.get_or_create(id=1, user=user, verified=True)

        # Login user.
        self.client.login(username=username, password=password)

    def test_editprofile_different_user(self):
        # Create and save user.
        user = CustomUser(
            first_name="Jerry",
            last_name="Seinfeld",
            date_of_birth="1954-04-29",
            gender="Man",
            email="jseinfeld@example.com",
        )
        user.save()

        # Try to edit another user's profile.
        get = "2"
        response = self.client.get("/u/" + get + "/edit")  # FIXME (use reverse())
        self.assertEqual(response.status_code, 403)


class MatchesViewTests(TestCase):
    def setUp(self):
        # Create and save user.
        username, password = "jspringer@example.com", "heyhey123"
        user = CustomUser.objects.create_user(username=username, password=password)
        EmailAddress.objects.get_or_create(id=1, user=user, verified=True)

        # Login user.
        self.client.login(username=username, password=password)

    def test_matches_basic(self):
        response = self.client.get(reverse("matches"))
        self.assertEqual(response.status_code, 200)


class Event_StackViewTests(TestCase):
    def setUp(self):
        # Create and save user.
        username, password = "jspringer@example.com", "heyhey123"
        user = CustomUser.objects.create_user(username=username, password=password)
        EmailAddress.objects.get_or_create(id=1, user=user, verified=True)

        # Login user.
        self.client.login(username=username, password=password)

    def test_event_stack_basic(self):
        response = self.client.get(reverse("matches"))
        self.assertEqual(response.status_code, 200)

    def test_squad(self):
        get = "?squad=1"
        response = self.client.get(reverse("matches") + get)
        self.assertEqual(response.status_code, 200)


class AuthenticatedViewTests(TestCase):
    def setUp(self):  # this logs in a test user for the subsequent test cases
        username = "testuser"
        password = "testpass"
        testuser = CustomUser.objects.create_user(username=username, password=password)
        EmailAddress.objects.get_or_create(id=1, user=testuser, verified=True)
        self.client.login(username=username, password=password)
        Concert.objects.get_or_create(
            id=1,
            performer_names="Team Debug Entities",
            venue_name="Rogers Hall",
            datetime=make_aware(
                datetime.datetime.strptime("2010-01-01T05:30", "%Y-%m-%dT%H:%M")
            ),
            borough="BK",
        )

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

    def test_authed_user_can_filter_events(self):
        get = (
            "?boroughs=BK&boroughs=MN&performers=test&venues=Rogers+Hall&"
            "venues=Elsewhere&genres=test&start_date=2010-10-30T17:30&"
            "end_date=2019-10-30T17:30&filter=#"
        )
        self.response = self.client.get(reverse("events") + get)
        self.assertEqual(self.response.status_code, 200)

    def test_user_cannot_access_nonexistent_profile(self):
        self.response = self.client.get(reverse("user", args=(9999,)))
        self.assertEqual(self.response.status_code, 403)

    def test_authed_user_can_see_matching_stack(self):
        self.response = self.client.get(reverse("event_stack", args=(1,)))
        self.assertEqual(self.response.status_code, 200)

    def test_authed_user_can_mark_interested_to_events(self):
        get = "?interested=1#"
        self.response = self.client.get(reverse("events") + get)
        self.assertEqual(self.response.status_code, 200)

    def test_authed_user_can_mark_going_to_events(self):
        get = "?going=1#"
        self.response = self.client.get(reverse("events") + get)
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
