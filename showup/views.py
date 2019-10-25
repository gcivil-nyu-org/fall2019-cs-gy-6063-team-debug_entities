import datetime

from .forms import CustomUserChangeForm
from .models import Concert
from django.contrib.auth.decorators import login_required
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
    if request.user.is_authenticated:
        return render(request, "user.html")
    else:
        return render(request, "home.html")


@login_required
def edit_profile(request, id):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse("user", kwargs={"id": id}))
    else:
        form = CustomUserChangeForm(instance=request.user)
        args = {"form": form}
        return render(request, "edit_profile.html", args)


def event_stack(request, eid):
    pass
