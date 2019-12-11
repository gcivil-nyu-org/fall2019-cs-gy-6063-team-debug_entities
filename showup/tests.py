import datetime
from dateutil.relativedelta import relativedelta

from .models import Concert, CustomUser, Genre, Request, Squad, Swipe
from allauth.account.admin import EmailAddress
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import make_aware, utc
from .forms import CustomUserForm


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

    def test_get_age_function_for_blank_birthday(self):
        blank_bday_user = CustomUser()
        self.assertEqual(blank_bday_user.get_age(), 0)

    def test_get_age_function_for_real_birthday(self):
        hundred_years_ago = (
            datetime.datetime.now() - relativedelta(years=100) - relativedelta(days=5)
        )
        real_bday_user = CustomUser(date_of_birth=hundred_years_ago)
        self.assertEqual(real_bday_user.get_age(), 100)


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


class SquadModelTests(TestCase):
    def test_Squad_basic(self):
        # Create a squad.
        s = Squad.objects.create(id=1)

        expected_output = f"{s.id}"
        self.assertEqual(s.__str__(), expected_output)


class RequestModelTests(TestCase):
    def test_request_basic(self):
        # Create a request.
        requester = Squad.objects.create(id=1)
        requestee = Squad.objects.create(id=2)
        r = Request.objects.create(requester=requester, requestee=requestee)

        expected_output = f"requester: {requester.id} requestee: {requestee.id}"
        self.assertEqual(r.__str__(), expected_output)


class HomeViewNotLoggedInTests(TestCase):
    def test_home_basic(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class HomeViewLoggedInTests(TestCase):
    def setUp(self):
        # Create and save user.
        email, password = "jkimmel@example.com", "heyhey123"
        squad_1 = Squad.objects.create(id=1)
        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, squad=squad_1
        )

        # Login user.
        EmailAddress.objects.create(id=1, user=user, verified=True)
        self.client.login(username=email, password=password)

        # Create and save event.
        Concert.objects.create(id=1, datetime=datetime.datetime.now(tz=utc))

    def test_home_interested(self):
        # Mark event as "Going".
        data = {"going": 1}
        self.client.post(reverse("events"), data=data)

        # Mark event as "Interested".
        data = {"eid": 1, "interested": ""}
        self.client.post(reverse("home"), data)

        num_interested = CustomUser.objects.get(id=1).squad.interested.count()
        self.assertEqual(num_interested, 1)

    def test_home_going(self):
        # Mark event as "Interested".
        data = {"interested": 1}
        self.client.post(reverse("events"), data=data)

        # Mark event as "Going".
        data = {"eid": 1, "going": ""}
        self.client.post(reverse("home"), data)

        num_going = CustomUser.objects.get(id=1).squad.going.count()
        self.assertEqual(num_going, 1)

    def test_home_not_interested(self):
        # Mark event as "Interested".
        data = {"interested": 1}
        self.client.post(reverse("events"), data=data)

        # Unmark event.
        data = {"eid": 1, "not_interested": ""}
        self.client.post(reverse("home"), data)

        num_interested = CustomUser.objects.get(id=1).squad.interested.count()
        self.assertEqual(num_interested, 0)

    def test_home_not_going(self):
        # Mark event as "Going".
        data = {"going": 1}
        self.client.post(reverse("events"), data=data)

        # Unmark event.
        data = {"eid": 1, "not_going": ""}
        self.client.post(reverse("home"), data)

        num_going = CustomUser.objects.get(id=1).squad.interested.count()
        self.assertEqual(num_going, 0)


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

    def test_events_interested_going(self):
        # if you're going to an event, and then mark that you're interested in
        # that event, the interested will overwrite the going
        self.client.post(reverse("events"), data={"going": 1})
        self.client.post(reverse("events"), data={"interested": 1})
        num_interested = CustomUser.objects.get(id=1).squad.interested.count()
        num_going = CustomUser.objects.get(id=1).squad.going.count()
        self.assertEqual(num_interested, 1)
        self.assertEqual(num_going, 0)

    def test_events_going_not_going(self):
        # if you mark yourself as going twice, you won't be going to the
        # event because the second one undoes the first one
        self.client.post(reverse("events"), data={"going": 1})
        self.client.post(reverse("events"), data={"going": 1})
        num_going = CustomUser.objects.get(id=1).squad.going.count()
        self.assertEqual(num_going, 0)


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
        Genre().save()
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

    def test_edit_profile_form_save(self):
        user = CustomUser.objects.get(id=1)
        self.assertEqual(user.bio, "")
        self.assertEqual(user.genres.count(), 0)
        data = {"bio": "Test bio", "genres": "1"}
        response = self.client.post(reverse("edit_profile", args=(1,)), data)
        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(id=1)
        self.assertEqual(user.bio, "Test bio")
        self.assertEqual(user.genres.count(), 1)


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

    def test_editsquad_already_in_squad(self):
        # Create form data.
        data = {"add": "", "email": "jkimmel@example.com"}

        # Send a POST request containing the form data.
        self.client.post(reverse("edit_squad", kwargs={"sid": 3}), data=data)

        # Ensure the POST request was successful.
        users = CustomUser.objects.filter(squad=3)
        self.assertEqual(users.count(), 1)

    def test_editsquad_email_does_not_exist(self):
        # Create form data.
        data = {"add": "", "email": "jseinfeld@example.com"}

        # Send a POST request containing the form data.
        self.client.post(reverse("edit_squad", kwargs={"sid": 3}), data=data)

        # Ensure the POST request was successful.
        users = CustomUser.objects.filter(squad=3)
        self.assertEqual(users.count(), 1)

    def test_editsquad_request_already_exists(self):
        # Create request.
        requester = Squad.objects.get(id=2)
        requestee = Squad.objects.get(id=3)
        Request.objects.create(requester=requester, requestee=requestee)

        # Try to add jfallon@example.com.
        data = {"add": "", "email": "jfallon@example.com"}
        self.client.post(reverse("edit_squad", kwargs={"sid": 3}), data=data)

        # Ensure the POST request was successful.
        users = CustomUser.objects.filter(squad=3)
        self.assertEqual(users.count(), 1)

    def test_editsquad_add_leave(self):
        # jfallon@example.com requests jkimmel@example.com to join their squad.
        requester = Squad.objects.get(id=2)
        requestee = Squad.objects.get(id=3)
        Request.objects.create(requester=requester, requestee=requestee)
        users = CustomUser.objects.filter(squad=2)
        self.assertEqual(users.count(), 1)

        # jkimmel@example.com accepts the request.
        data = {"accept": "", "their_sid": 2}
        self.client.post(reverse("requests"), data=data)
        users = CustomUser.objects.filter(squad=2)
        self.assertEqual(users.count(), 2)

        # jkimmel@example.com leaves their squad.
        data = {"leave": ""}
        self.client.post(reverse("edit_squad", kwargs={"sid": 2}), data=data)

        # Ensure the POST request was successful.
        user = CustomUser.objects.get(squad=2)
        self.assertEqual(user.email, "jfallon@example.com")

    def test_editsquad_add_twice(self):
        # jkimmel@example.com requests jfallon@example.com to join their squad.
        data = {"add": "", "email": "jfallon@example.com"}
        self.client.post(reverse("edit_squad", kwargs={"sid": 3}), data=data)

        # jkimmel@example.com requests jfallon@example.com to join their squad.
        data = {"add": "", "email": "jfallon@example.com"}
        self.client.post(reverse("edit_squad", kwargs={"sid": 3}), data=data)

        # Ensure the POST request was successful.
        user = CustomUser.objects.get(squad=3)
        self.assertEqual(user.email, "jkimmel@example.com")

    def test_editsquad_leave_one(self):
        # Create form data.
        data = {"leave": ""}

        # Send a POST request containing the form data.
        response = self.client.post(reverse("edit_squad", kwargs={"sid": 3}), data=data)

        # Ensure the POST request returns PermissionDenied.
        self.assertEqual(response.status_code, 403)

    def test_editsquad_malformed_post(self):
        # Create form data.
        data = {"remove": ""}

        # Send a POST request containing the form data.
        response = self.client.post(reverse("edit_squad", kwargs={"sid": 3}), data=data)

        # Ensure the POST request returns PermissionDenied.
        self.assertEqual(response.status_code, 403)

    def test_editsquad_get(self):
        # Send a GET request.
        response = self.client.get(reverse("edit_squad", kwargs={"sid": 3}))

        # Ensure the POST request was successful.
        self.assertEqual(response.status_code, 200)

    def test_editsquad_edit_other_squad(self):
        # Create form data.
        data = {"add": "", "email": "jspringer@example.com"}

        # Send a POST request containing the form data.
        response = self.client.post(reverse("edit_squad", kwargs={"sid": 2}), data=data)

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

    def test_authed_user_can_see_messages_with_squad_ids_in_reverse_order(self):
        self.client.login(username="jfallon@example.com", password="heyhey123")
        self.response = self.client.get(reverse("messages", args=(2, 1)))
        self.assertEqual(
            self.response.context["iframe_url"],
            "https://showup-nyc-messaging.herokuapp.com/1-2",
        )  # test that the view correctly puts the smaller squad ID first
        self.assertEqual(self.response.status_code, 200)

    def test_authed_user_cannot_see_messages_with_squad_they_havent_matched_with(self):
        Squad().save()
        self.response = self.client.get(reverse("messages", args=(1, 3)))
        self.assertEqual(self.response.status_code, 403)


class SettingsViewTests(TestCase):
    def setUp(self):
        # Create and save user.
        username, password = "tom.hanks@hollywood.com", "TomHanks123"
        date_of_birth = datetime.datetime(1954, 4, 29).date()
        squad = Squad()
        squad.save()
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            date_of_birth=date_of_birth,
            squad=squad,
        )
        user.save()
        EmailAddress.objects.get_or_create(id=1, user=user, verified=True)

        # Login user.
        self.client.login(username=username, password=password)

        # Create and save event.
        event = Concert(id=1, datetime=datetime.datetime.now(tz=utc), borough="BK")
        event.save()

    def test_save_form(self):
        # check if the user has first_name, last_name as empty string
        user = CustomUser.objects.get(id=1)
        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")
        data = {
            "first_name": "Tom",
            "last_name": "Hanks",
            "email": "tom.hanks@hollywood.com",
        }
        # Send a POST request containing the first_name, last_name
        response = self.client.post(reverse("settings"), data)
        self.assertEqual(response.status_code, 200)
        # Ensure the POST request was successful.
        user = CustomUser.objects.get(id=1)
        self.assertEqual(user.first_name, "Tom")
        self.assertEqual(user.last_name, "Hanks")


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

    def test_requests_add_interested(self):
        # Create a request.
        squad_1 = Squad.objects.get(id=1)
        squad_3 = Squad.objects.get(id=3)
        Request.objects.create(requester=squad_1, requestee=squad_3)

        # Have bigger squad be interested in an event that smaller squad is
        # neither interested in or going to.
        event = Concert.objects.create(id=1, datetime=datetime.datetime.now(tz=utc))
        squad_3.interested.add(event)
        squad_3.save()

        # Accept the request.
        data = {"accept": "", "their_sid": 1}
        self.client.post(reverse("requests"), data=data)

        # Little squad should be interested in one event.
        # Remember that the squad with the larger id is deleted!
        squad_1 = Squad.objects.get(id=1)
        self.assertEqual(len(squad_1.interested.all()), 1)

    def test_requests_add_going(self):
        # Create a request.
        squad_1 = Squad.objects.get(id=1)
        squad_3 = Squad.objects.get(id=3)
        Request.objects.create(requester=squad_1, requestee=squad_3)

        # Have smaller squad be interested in an event that bigger squad is going to.
        event = Concert.objects.create(id=1, datetime=datetime.datetime.now(tz=utc))
        squad_1.interested.add(event)
        squad_1.save()
        squad_3.going.add(event)
        squad_3.save()

        # Have bigger squad be going to an event that smaller squad is neither
        # interested in or going to.
        event = Concert.objects.create(id=2, datetime=datetime.datetime.now(tz=utc))
        squad_3.going.add(event)
        squad_3.save()

        # Accept the request.
        data = {"accept": "", "their_sid": 1}
        self.client.post(reverse("requests"), data=data)

        # Little squad should be going to two events.
        # Remember that the squad with the larger id is deleted!
        squad_1 = Squad.objects.get(id=1)
        self.assertEqual(len(squad_1.going.all()), 2)


class EventStackViewTests(TestCase):
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

    def test_eventstack_one_swipe(self):
        # Create an event.
        Concert.objects.create(id=1, datetime=datetime.datetime.now(tz=utc))

        # Submit a swipe.
        data = {"their_sid": 1, "match": True}
        self.client.post(reverse("event_stack", kwargs={"eid": 1}), data=data)

        # Ensure the swipe exists.
        swipe = Swipe.objects.get(event=1, swiper_id=3, swipee_id=1)
        expected_output = "Swiper: 3, Swipee: 1, Event: 1, Direction: True"
        self.assertEqual(swipe.__str__(), expected_output)

    def test_eventstack_both_swipe_no_match(self):
        # Create an event.
        e = Concert.objects.create(id=1, datetime=datetime.datetime.now(tz=utc))

        # Create a swipe.
        Swipe.objects.create(event=e, swiper_id=1, swipee_id=3, direction=False)

        # Submit a swipe.
        data = {"their_sid": 1, "match": True}
        self.client.post(reverse("event_stack", kwargs={"eid": 1}), data=data)

        # Ensure the swipes exist.
        swipe = Swipe.objects.get(event=1, swiper_id=1, swipee_id=3)
        expected_output = "Swiper: 1, Swipee: 3, Event: 1, Direction: False"
        self.assertEqual(swipe.__str__(), expected_output)

        swipe = Swipe.objects.get(event=1, swiper_id=3, swipee_id=1)
        expected_output = "Swiper: 3, Swipee: 1, Event: 1, Direction: True"
        self.assertEqual(swipe.__str__(), expected_output)


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

    def test_authed_user_can_swipe_on_matching_stack(self):
        data = {"their_sid": 1, "match": "True"}
        self.client.post(reverse("event_stack", args=(1,)), data=data)
        num_swipes = Swipe.objects.count()
        self.assertEqual(num_swipes, 1)

    def test_authed_user_can_swipe_on_squad_that_has_not_swiped_on_them(self):
        Squad().save()
        data = {"their_sid": 2, "match": "True"}
        self.client.post(reverse("event_stack", args=(1,)), data=data)
        num_swipes = Swipe.objects.count()
        self.assertEqual(num_swipes, 1)

    def test_authed_user_can_swipe_left(self):
        data = {"their_sid": 1, "match": "False"}
        self.client.post(reverse("event_stack", args=(1,)), data=data)
        num_swipes = Swipe.objects.count()
        self.assertEqual(num_swipes, 1)

    def test_eligible_squads_are_shown_on_stack(self):
        s = Squad()
        s.save()
        s.interested.add(Concert.objects.get(id=1))
        self.response = self.client.get(reverse("event_stack", args=(1,)))
        self.assertEqual(self.response.status_code, 200)

    def test_authed_user_can_mark_interested_to_events(self):
        self.client.post(reverse("events"), data={"interested": 1})
        num_interested = CustomUser.objects.get(id=1).squad.interested.count()
        self.assertEqual(num_interested, 1)

    def test_authed_user_can_mark_going_to_events(self):
        self.client.post(reverse("events"), data={"going": 1})
        num_going = CustomUser.objects.get(id=1).squad.going.count()
        self.assertEqual(num_going, 1)

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


class CustomUserFormTests(TestCase):
    def test_valid_data(self):
        data = {
            "first_name": "tom",
            "last_name": "hanks",
            "date_of_birth": "2019-01-01",
            "email": "tom.hanks@hollywood.com",
        }
        form = CustomUserForm(data=data)
        self.assertTrue(form.is_valid())
