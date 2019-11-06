import datetime

from .forms import CustomUserChangeForm
from .models import Concert, CustomUser, Swipe
from allauth.account.admin import EmailAddress
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, reverse
from django.utils.timezone import make_aware


def home(request):
    return render(request, "home.html")


def get_performers():
    performer_names_choices = []
    for performer in Concert.objects.all().values("performer_names"):
        performer_names_choices.extend(performer["performer_names"].split(","))

    performer_names_choices = [name.strip(" ") for name in performer_names_choices]
    performer_names_choices = list(set(performer_names_choices))
    performer_names_choices.sort()
    return performer_names_choices


def get_venues():
    venue_name_choices = []
    for venue in Concert.objects.all().values("venue_name"):
        venue_name_choices.extend([venue["venue_name"]])

    venue_name_choices = [name.strip(" ") for name in venue_name_choices]
    venue_name_choices = list(set(venue_name_choices))
    venue_name_choices.sort()
    return venue_name_choices


def get_genres():
    genre_choices = []
    for genre in Concert.objects.all().values("genres"):
        genre_choices.extend(genre["genres"].split(", "))

    genre_choices = [name.strip(" ") for name in genre_choices]
    genre_choices = list(set(genre_choices))
    genre_choices.sort()
    return genre_choices


@login_required
def events(request):
    events = Concert.objects.all()
    start_date = make_aware(datetime.datetime.today())
    end_date = make_aware(datetime.datetime(datetime.MAXYEAR, 12, 31, 23, 59))
    events = events.filter(datetime__gte=start_date, datetime__lte=end_date).order_by(
        "datetime"
    )
    borough_choices = Concert.BOROUGH_CHOICES
    performer_names_choices = get_performers()
    venue_name_choices = get_venues()
    genre_choices = get_genres()

    # User clicks "Filter"
    if "filter" in request.GET:
        # filter boroughs
        if "boroughs" in request.GET:
            events = events.filter(borough__in=request.GET.getlist("boroughs"))

        # filter performers. only 1 performer at the moment
        if "performers" in request.GET:
            events = events.filter(performer_names__contains=request.GET["performers"])

        # filter venues
        if "venues" in request.GET:
            events = events.filter(venue_name__in=request.GET.getlist("venues"))

        # filter genres. only 1 genre at the moment
        if "genres" in request.GET:
            events = events.filter(genres__contains=request.GET["genres"])

        # filter start-date
        if request.GET["start_date"] != "":
            start_date = make_aware(
                datetime.datetime.strptime(request.GET["start_date"], "%Y-%m-%dT%H:%M")
            )
            events = events.filter(datetime__gte=start_date, datetime__lte=end_date)

        # filter end-date
        if request.GET["start_date"] != "":
            end_date = make_aware(
                datetime.datetime.strptime(request.GET["end_date"], "%Y-%m-%dT%H:%M")
            )
            events = events.filter(datetime__gte=start_date, datetime__lte=end_date)

    # User clicked "Interested" button.
    if "interested" in request.GET:
        event_id = request.GET.get("interested")
        request.user.interested.add(event_id)

    # User clicked "Going" button.
    if "going" in request.GET:
        event_id = request.GET.get("going")
        request.user.going.add(event_id)

    return render(
        request,
        "events.html",
        {
            "events": events,
            "borough_choices": borough_choices,
            "performer_names_choices": performer_names_choices,
            "venue_choices": venue_name_choices,
            "genre_choices": genre_choices,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


@login_required
def user(request, id):
    try:  # check if given id exists
        requested_user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        raise PermissionDenied

    if not EmailAddress.objects.get(id=id).verified:
        raise PermissionDenied

    return render(request, "user.html", context={"requested_user": requested_user})


@login_required
def edit_profile(request, id):
    if request.user.id == id:
        # above, on the left is the user's id, on the right is the id in the URL
        form = CustomUserChangeForm(request.POST or None, instance=request.user)
        if request.method == "POST" and form.is_valid():
            form.save()
            return redirect(reverse("user", kwargs={"id": id}))
        return render(request, "edit_profile.html", {"form": form})
    else:
        raise PermissionDenied


@login_required
def event_stack(request, eid):
    my_id = request.user.id
    id_to_send = request.user.id
    popup = 0
    """
    Gather all the eligible users to return.
    Criteria:
    1. They're interested in or going to the event
    2. They haven't swiped left on me
    3. I haven't swiped on them in any direction
    4. They're not me
    """
    users = CustomUser.objects.filter(interested__id=eid) | CustomUser.objects.filter(
        going__id=eid
    )  # criterion 1
    IDs_swiped_left_on_me = [
        i.swiper.id
        for i in Swipe.objects.filter(swipee__id=my_id, event__id=eid, direction=False)
    ]  # criterion 2
    IDs_I_swiped = [
        i.swipee.id for i in Swipe.objects.filter(swiper__id=my_id, event__id=eid)
    ]  # criterion 3
    users = [
        u
        for u in users
        if u.id not in IDs_swiped_left_on_me
        and u.id not in IDs_I_swiped
        and u.id != my_id
    ]  # criterion 4
    # our filtering is done, users is the list of users who should be shown for swiping

    if request.method == "POST":  # user is submitting a swipe
        swipee_id = request.POST["swipee_id"]
        my_direction = True if request.POST["match"] == "True" else False
        Swipe.objects.get_or_create(  # write user's swipe to the database
            swiper=CustomUser(id=my_id),
            swipee=CustomUser(id=swipee_id),
            event=Concert(id=eid),
            direction=my_direction,
        )

        """
        Figure out if a match happened
        Criteria:
        1. The swipe that just happened was to the right
        2. The swipee has previously swiped right on the swiper
        """
        try:
            their_swipe_on_me = Swipe.objects.get(
                swiper__id=swipee_id, swipee__id=my_id, event__id=eid
            )

        except Swipe.DoesNotExist:
            their_swipe_on_me = None

        # the line below checks criteria 1 and 2
        if my_direction and their_swipe_on_me and their_swipe_on_me.direction:
            popup = 1
            id_to_send = their_swipe_on_me.swiper_id
            print(f"Users {my_id} and {swipee_id} just matched")

    return render(request, "match.html",
                  {
                    "users": users,
                    "popup": popup,
                    "id_to_send": id_to_send
                  }
                  )
