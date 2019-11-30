from .forms import CustomUserChangeForm, SquadForm, CustomUserForm
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
    filter = ConcertFilter(request.GET, queryset=Concert.objects.all())
    context = {
        "filter": filter,
        "interested_list": request.user.interested.values_list("id", flat=True),
        "going_list": request.user.going.values_list("id", flat=True),
        "unique_genres": [g.genre for g in Genre.objects.all()],
        "unique_venues": set([c.venue_name for c in Concert.objects.all()]),
        "unique_performers": set([c.performer_names for c in Concert.objects.all()]),
        "boroughs": Concert.BOROUGH_CHOICES,
    }
    # User clicked "Interested" button.
    if "interested" in request.GET:
        insert_to_list_exclusively(
            request.GET.get("interested"), request.user.interested, request.user.going
        )
    # User clicked "Going" button.
    elif "going" in request.GET:
        insert_to_list_exclusively(
            request.GET.get("going"), request.user.going, request.user.interested
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
    # My uid.
    uid = request.user.id

    # Get the users interested in or going to the event.
    users = CustomUser.objects.filter(interested__id=eid) | CustomUser.objects.filter(
        going__id=eid
    )

    # These are the users that swiped left on me.
    swiped_left = [
        x.swiper.id
        for x in Swipe.objects.filter(event__id=eid, swipee__id=uid, direction=False)
    ]

    # These are the users that I swiped on.
    swiped = [x.swipee.id for x in Swipe.objects.filter(event__id=eid, swiper__id=uid)]

    # Exclude the users that swiped left on me, the users that I swiped on, and
    # myself.
    users = [
        u
        for u in users
        if u.id not in swiped_left and u.id not in swiped and u.id != uid
    ]

    return users


@login_required
def event_stack(request, eid):
    my_id = request.user.id
    match = CustomUser.objects.get(id=request.user.id)
    popup = 0
    users = get_stack(request, eid)

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
            match = CustomUser.objects.get(id=their_swipe_on_me.swiper_id)

        # Update users.
        users = get_stack(request, eid)

    return render(
        request, "match.html", {"users": users, "popup": popup, "match": match}
    )


@login_required
def matches(request):
    # My uid.
    uid = request.user.id
    uniq_events = set()

    # The users that I swiped right on.
    i_swiped_right = [x for x in Swipe.objects.filter(swiper__id=uid, direction=True)]

    # The users that swiped right on me.
    they_swiped_right = [
        x.swiper for x in Swipe.objects.filter(swipee__id=uid, direction=True)
    ]

    # The intersection of the above two.
    matches = [x for x in i_swiped_right if x.swipee in they_swiped_right]
    matches.sort(key=lambda x: x.event.id)
    for match in matches:
        uniq_events.add(match.event)

    return render(request, "matches.html", {"matches": matches, "events": uniq_events})


@login_required
def settings(request):
    if request.POST.get("save_button") == "save":
        form = CustomUserForm(request.POST or None, instance=request.user)
        if form.is_valid():
            try:
                form.save(request)
            except Exception as ex:
                print("hit exception")
                print(ex)

    return render(request, "settings.html", {"user": request.user})
