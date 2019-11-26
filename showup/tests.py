import datetime

from .models import Concert, CustomUser, Genre, Request, Squad, Swipe
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
        squad_1 = Squad.objects.create()
        CustomUser.objects.create(
            username="1", email="swiper@example.com", squad=squad_1
        )

        squad_2 = Squad.objects.create()
        CustomUser.objects.create(
            username="2", email="swipee@example.com", squad=squad_2
        )

        event = Concert.objects.create(id=1, datetime=datetime.datetime.now(tz=utc))

        direction = True

        # Create the Swipe object.
        swipe = Swipe.objects.create(
            swiper=squad_1, swipee=squad_2, event=event, direction=direction
        )

        expected_output = (
            f"Swiper: {squad_1.id}, "
            f"Swipee: {squad_2.id}, "
            f"Event: {event.id}, "
            f"Direction: {direction}"
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
        squad = Squad()
        squad.save()
        user = CustomUser.objects.create_user(
            username=username, password=password, squad=squad
        )
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


class SquadViewTests(TestCase):
    def setUp(self):
        # Create and save user.
        username, password = "jspringer@example.com", "heyhey123"
        squad = Squad(id=1)
        squad.save()
        user = CustomUser.objects.create_user(
            username=username, password=password, squad=squad
        )
        EmailAddress.objects.get_or_create(id=1, user=user, verified=True)

        # Login user.
        self.client.login(username=username, password=password)

    def test_squad_basic(self):
        response = self.client.get(reverse("squad", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_squad_does_not_exist(self):
        response = self.client.get(reverse("squad", args=(2,)))
        self.assertEqual(response.status_code, 403)


class EditSquadViewTests(TestCase):
    def setUp(self):
        # Create and save user one.
        email, password = "jspringer@example.com", "heyhey123"
        squad = Squad.objects.create(id=1)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad
        )

        # Login user one.
        EmailAddress.objects.create(id=1, user=user, verified=True)
        self.client.login(username=email, password=password)

        # Create and save user two.
        email, password = "jfallon@example.com", "heyhey123"
        squad = Squad.objects.create(id=2)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad
        )

        # Create and save user three.
        email, password = "jkimmel@example.com", "heyhey123"
        squad = Squad.objects.create(id=3)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad
        )

    def test_editsquad_already_in_squad(self):
        # Create form data.
        data = {"add": "", "email": "jspringer@example.com"}

        # Send a POST request containing the form data.
        self.client.post(reverse("edit_squad", kwargs={"id": 1}), data=data)

        # Ensure the POST request was successful.
        users = CustomUser.objects.filter(squad=1)
        self.assertEqual(users.count(), 1)

    def test_editsquad_email_does_not_exist(self):
        # Create form data.
        data = {"add": "", "email": "jseinfeld@example.com"}

        # Send a POST request containing the form data.
        self.client.post(reverse("edit_squad", kwargs={"id": 1}), data=data)

        # Ensure the POST request was successful.
        users = CustomUser.objects.filter(squad=1)
        self.assertEqual(users.count(), 1)

    def test_editsquad_add_leave(self):
        # jspringer@example.com requests jfallon@example.com to join their squad.
        data = {"add": "", "email": "jfallon@example.com"}
        self.client.post(reverse("edit_squad", kwargs={"id": 1}), data=data)
        users = CustomUser.objects.filter(squad=1)
        self.assertEqual(users.count(), 1)

        # jfallon@example.com requests jspringer@example.com to join their squad.
        requester = Squad.objects.get(id=2)
        requestee = Squad.objects.get(id=1)
        Request.objects.create(requester=requester, requestee=requestee)

        # jspringer@example.com requests jfallon@example.com to join their squad.
        data = {"add": "", "email": "jfallon@example.com"}
        self.client.post(reverse("edit_squad", kwargs={"id": 1}), data=data)
        users = CustomUser.objects.filter(squad=1)
        self.assertEqual(users.count(), 2)

        # jspringer@example.com leaves their squad.
        data = {"leave": ""}
        self.client.post(reverse("edit_squad", kwargs={"id": 1}), data=data)

        # Ensure the POST request was successful.
        user = CustomUser.objects.get(squad=1)
        self.assertEqual(user.email, "jfallon@example.com")

    def test_editsquad_leave_one(self):
        # Create form data.
        data = {"leave": ""}

        # Send a POST request containing the form data.
        response = self.client.post(reverse("edit_squad", kwargs={"id": 1}), data=data)

        # Ensure the POST request returns PermissionDenied.
        self.assertEqual(response.status_code, 403)

    def test_editsquad_malformed_post(self):
        # Create form data.
        data = {"remove": ""}

        # Send a POST request containing the form data.
        response = self.client.post(reverse("edit_squad", kwargs={"id": 1}), data=data)

        # Ensure the POST request returns PermissionDenied.
        self.assertEqual(response.status_code, 403)

    def test_editsquad_get(self):
        # Send a GET request.
        response = self.client.get(reverse("edit_squad", kwargs={"id": 1}))

        # Ensure the POST request was successful.
        self.assertEqual(response.status_code, 200)

    def test_editsquad_edit_other_squad(self):
        # Create form data.
        data = {"add": "", "email": "jfallon@example.com"}

        # Send a POST request containing the form data.
        response = self.client.post(reverse("edit_squad", kwargs={"id": 2}), data=data)

        # Ensure the POST request returns PermissionDenied.
        self.assertEqual(response.status_code, 403)


class MatchesViewTests(TestCase):
    def setUp(self):
        # Create and save user one.
        email, password = "jspringer@example.com", "heyhey123"
        squad_1 = Squad.objects.create(id=1)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad_1
        )

        # Login user one.
        EmailAddress.objects.create(id=1, user=user, verified=True)
        self.client.login(username=email, password=password)

        # Create and save user two.
        email, password = "jfallon@example.com", "heyhey123"
        squad_2 = Squad.objects.create(id=2)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad_2
        )

        # Create needed objects for Swipe model.
        event = Concert.objects.create(id=1, datetime=datetime.datetime.now(tz=utc))
        direction = True

        # Create the Swipe objects.
        Swipe.objects.create(
            swiper=squad_1, swipee=squad_2, event=event, direction=direction
        )
        Swipe.objects.create(
            swiper=squad_2, swipee=squad_1, event=event, direction=direction
        )

    def test_matches_basic(self):
        response = self.client.get(reverse("matches"))
        self.assertEqual(response.status_code, 200)

    def test_authed_user_can_see_messages(self):
        self.response = self.client.get(reverse("messages", args=(1, 2)))
        self.assertEqual(
            self.response.context["iframe_url"],
            "https://showup-nyc-messaging.herokuapp.com/1-2",
        )  # test that the view correctly puts the smaller squad ID first
        self.assertEqual(self.response.status_code, 200)


class RequestsViewTests(TestCase):
    def setUp(self):
        # Create and save user one.
        email, password = "jspringer@example.com", "heyhey123"
        squad_1 = Squad.objects.create(id=1)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad_1
        )

        # Create and save user two.
        email, password = "jfallon@example.com", "heyhey123"
        squad_2 = Squad.objects.create(id=2)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad_2
        )

        # Create and save user three.
        email, password = "jkimmel@example.com", "heyhey123"
        squad_3 = Squad.objects.create(id=3)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad_3
        )

        # Login user three.
        EmailAddress.objects.create(id=3, user=user, verified=True)
        self.client.login(username=email, password=password)

    def test_requests_get(self):
        self.response = self.client.get(reverse("requests"))
        self.assertEqual(self.response.status_code, 200)

    def test_requests_get_multiple(self):
        # Create the request.
        squad_1 = Squad.objects.get(id=1)
        squad_3 = Squad.objects.get(id=3)
        Request.objects.create(requester=squad_1, requestee=squad_3)

        # Create the request.
        squad_2 = Squad.objects.get(id=2)
        Request.objects.create(requester=squad_2, requestee=squad_3)

        self.response = self.client.get(reverse("requests"))
        self.assertEqual(self.response.status_code, 200)

    def test_requests_accept(self):
        # Create the request.
        squad_1 = Squad.objects.get(id=1)
        squad_3 = Squad.objects.get(id=3)
        Request.objects.create(requester=squad_1, requestee=squad_3)

        # Create form data.
        data = {"accept": "", "their_sid": 1}

        # Send a POST request containing the form data.
        self.client.post(reverse("requests"), data=data)

        squad_size = CustomUser.objects.filter(squad=squad_1).count()
        self.assertEqual(squad_size, 2)

    def test_requests_deny(self):
        # Create the request.
        squad_1 = Squad.objects.get(id=1)
        squad_3 = Squad.objects.get(id=3)
        Request.objects.create(requester=squad_1, requestee=squad_3)

        # Create form data.
        data = {"deny": "", "their_sid": 1}

        # Send a POST request containing the form data.
        self.client.post(reverse("requests"), data=data)

        squad_size = CustomUser.objects.filter(squad=squad_1).count()
        self.assertEqual(squad_size, 1)

    def test_requests_malformed(self):
        # Create the request.
        squad_1 = Squad.objects.get(id=1)
        squad_3 = Squad.objects.get(id=3)
        Request.objects.create(requester=squad_1, requestee=squad_3)

        # Create form data.
        data = {"malformed": "", "their_sid": 1}

        # Send a POST request containing the form data.
        self.client.post(reverse("requests"), data=data)

        squad_size = CustomUser.objects.filter(squad=squad_1).count()
        self.assertEqual(squad_size, 1)


class AuthenticatedViewTests(TestCase):
    def setUp(self):  # this logs in a test user for the subsequent test cases
        username = "testuser"
        password = "testpass"
        squad = Squad()
        squad.save()
        testuser = CustomUser.objects.create_user(
            username=username, password=password, squad=squad
        )
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

    def test_authed_user_cannot_see_messages_page_with_different_squad_id(self):
        self.response = self.client.get(reverse("messages", args=(25, 1)))
        self.assertEqual(self.response.status_code, 403)
        # the test user can't access this page because their squad ID is not 25


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
