from .forms import CustomUserChangeForm, SquadForm
from .models import Concert, CustomUser, Genre, Squad, Swipe
from allauth.account.admin import EmailAddress
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, reverse
from .filters import ConcertFilter


def home(request):
    return render(request, "home.html")


@login_required
def events(request):
    # My squad.
    squad = request.user.squad

    filter = ConcertFilter(request.GET, queryset=Concert.objects.all())
    context = {
        "filter": filter,
        "interested_list": squad.interested.values_list("id", flat=True),
        "going_list": squad.going.values_list("id", flat=True),
        "unique_genres": [g.genre for g in Genre.objects.all()],
        "unique_venues": set([c.venue_name for c in Concert.objects.all()]),
        "unique_performers": set([c.performer_names for c in Concert.objects.all()]),
        "boroughs": Concert.BOROUGH_CHOICES,
    }

    # User clicked "Interested" button.
    if "interested" in request.GET:
        insert_to_list_exclusively(
            request.GET.get("interested"), squad.interested, squad.going
        )

    # User clicked "Going" button.
    if "going" in request.GET:
        insert_to_list_exclusively(
            request.GET.get("going"), squad.going, squad.interested
        )

    return render(request, "events.html", context=context)


def insert_to_list_exclusively(event_id, add_list, remove_list):
    if add_list.filter(id=event_id).count() > 0:
        add_list.remove(event_id)
    else:
        add_list.add(event_id)
        if remove_list.filter(id=event_id).count() > 0:
            remove_list.remove(event_id)


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
def squad(request, id):
    try:
        squad = Squad.objects.get(id=id)
        users = CustomUser.objects.filter(squad=squad)
    except Squad.DoesNotExist:
        raise PermissionDenied

    return render(request, "squad.html", context={"users": users})


@login_required
def edit_squad(request, id):
    # You can only edit your own squad.
    if request.user.squad.id == id:
        form = SquadForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            # Get my squad.
            my_squad = request.user.squad

            # Get their squad and their members.
            try:
                their_squad = CustomUser.objects.get(email=request.POST["email"]).squad

                # We are already in the same squad.
                if my_squad.id == their_squad.id:
                    # TODO: Output some sort of message.
                    return render(request, "edit_squad.html", {"form": form})

                their_members = CustomUser.objects.filter(squad=their_squad)
            except CustomUser.DoesNotExist:
                # TODO: Output some sort of message.
                return render(request, "edit_squad.html", {"form": form})

            # Merge squads.
            for member in their_members:
                member.squad = my_squad
                member.save()

            # Delete their old squad.
            Squad.objects.get(id=their_squad.id).delete()

            return redirect(reverse("squad", kwargs={"id": id}))
        return render(request, "edit_squad.html", {"form": form})
    else:
        raise PermissionDenied


def get_stack(request, eid):
    # My sid.
    sid = request.squad.id

    # Get the squads interested in or going to the event.
    squads = Squad.objects.filter(interested__id=eid) | Squad.objects.filter(
        going__id=eid
    )

    # These are the squads that swiped left on my squad.
    swiped_left = [
        x.swiper.id
        for x in Swipe.objects.filter(swipee__id=sid, event__id=eid, direction=False)
    ]

    # These are the squads that my squad swiped on.
    swiped = [x.swipee.id for x in Swipe.objects.filter(swiper__id=sid, event__id=eid)]

    """
    Exclude the following squads:
    - The squads that swiped left on my squad.
    - The squads that my squad swiped on.
    - My squad.
    """
    squads = [
        s
        for s in squads
        if s.id not in swiped_left and s.id not in swiped and s.id != sid
    ]

    return squads


@login_required
def event_stack(request, eid):
    if request.method == "POST":
        # Create a Swipe object.
        my_sid = request.squad.id
        their_sid = request.POST["swipee_id"]
        direction = True if request.POST["match"] == "True" else False

        my_swipe = Swipe.objects.create(
            swiper=Squad(id=my_sid),
            swipee=Squad(id=their_sid),
            event=Concert(id=eid),
            direction=direction,
        )

        # Check to see if their squad swiped on our squad.
        their_swipe = Swipe.objects.filter(
            swiper__id=their_sid, swipee__id=my_sid, event__id=eid
        )
        if their_swipe.exists():
            if my_swipe.direction and their_swipe.direction:
                match = Squad.objects.get(id=their_sid)
            else:
                match = None
    else:
        match = None

    squads = get_stack(request, eid)
    return render(request, "match.html", {"squads": squads, "match": match})


@login_required
def matches(request):
    # My uid.
    sid = request.user.squad.id

    # The squads that my squad swiped right on.
    i_swiped_right = [x for x in Swipe.objects.filter(swiper__id=sid, direction=True)]

    # The squads that swiped right on my squad.
    they_swiped_right = [
        x.swiper for x in Swipe.objects.filter(swipee__id=sid, direction=True)
    ]

    # The intersection of the above two.
    uniq_events = set()
    matches = [x for x in i_swiped_right if x.swipee in they_swiped_right]
    matches.sort(key=lambda x: x.event.id)
    for match in matches:
        uniq_events.add(match.event)

    return render(request, "matches.html", {"matches": matches, "events": uniq_events})
