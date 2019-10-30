import datetime

from .forms import CustomUserChangeForm
from .models import Concert, CustomUser, Match
from allauth.account.admin import EmailAddress
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
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
        if request.method == "POST":
            form = CustomUserChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect(reverse("user", kwargs={"id": id}))
        else:
            form = CustomUserChangeForm(instance=request.user)
            args = {"form": form}
            return render(request, "edit_profile.html", args)
    else:
        raise PermissionDenied


@login_required
def event_stack(request, eid):

    if request.method == "POST":
        # Maintain the Match model constraint.
        if request.user.id < request.uid:
            uid_1 = request.user.id
            uid_2 = request.uid
        else:
            uid_1 = request.uid
            uid_2 = request.user.id

        # Get the row from Match if it exists, otherwise create it.
        try:
            row = Match.objects.get(uid_1=uid_1, uid_2=uid_2, eid=eid)
        except Match.MultipleObjectsReturned as e:
            print(e)
        except Match.DoesNotExist:
            row = Match(uid_1=uid_1, uid_2=uid_2, eid=eid)

        # Write decision to row.
        if request.user.id < request.uid:
            # User swiped right.
            if "True" in request.GET:
                decision_1 = True

            # User swiped left.
            if "False" in request.GET:
                decision_1 = False

            # Write to row.
            row.decision_1 = decision_1
        else:
            # User swiped right.
            if "True" in request.GET:
                decision_2 = True

            # User swiped left.
            if "False" in request.GET:
                decision_2 = False

            # Write to row.
            row.decision_2 = decision_2

        # Figure out if there is a match.
        if row.decision_1 is not None and row.decision_2 is not None:
            if row.decision_1 and row.decision_2:  # TT
                # uid_1 and uid_2 match.
                row.decision = True

                # TODO: Vedanth's code goes here.

            else:
                # uid_1 and uid_2 do not match.
                row.decision = False

                # TODO: Vedanth's code goes here.

        row.save()
        return render(request, "match.html")
    else:
        # This user's id.
        uid = request.user.id

        # All relationships that exist between this user and all other users
        # for this event where a decision has not yet been made.
        matches = Match.objects.filter(
            (Q(uid_1=uid) | Q(uid_2=uid)) & Q(eid=eid) & Q(decision=None)
        )

        matches_copy = matches
        for match in matches_copy:
            # Check to see if uid_1 and uid_2 are interested in/going to event.
            uid_1 = CustomUser.objects.filter(
                Q(id=match.uid_1), (Q(interested__id=eid) | Q(going__id=eid))
            ).exists()
            uid_2 = CustomUser.objects.filter(
                Q(id=match.uid_2), (Q(interested__id=eid) | Q(going__id=eid))
            ).exists()

            # One of the users is not interested in/going to event, remove.
            if not uid_1 or not uid_2:
                matches = matches.exclude(uid_1=match.uid_1, uid_2=match.uid_2)

        # Gather all the other users to return.
        users = []
        for match in matches:
            # Get the CustomUser objects.
            uid_1 = CustomUser.objects.get(id=match.uid_1)
            uid_2 = CustomUser.objects.get(id=match.uid_2)

            # Add the other user to users.
            if uid == uid_1.id:
                users.append(uid_2)
            if uid == uid_2.id:
                users.append(uid_1)

        args = {"users": users}
        return render(request, "match.html", args)
