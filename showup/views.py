from .forms import CustomUserChangeForm
from .models import Concert, CustomUser, Swipe
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

    return render(
        request,
        "match.html",
        {"users": users, "popup": popup, "id_to_send": id_to_send},
    )


@login_required
def matches(request):
    # My uid.
    uid = request.user.id

    # The users that I swiped right on.
    i_swiped_right = [x for x in Swipe.objects.filter(swiper__id=uid, direction=True)]

    # The users that swiped right on me.
    they_swiped_right = [
        x.swiper for x in Swipe.objects.filter(swipee__id=uid, direction=True)
    ]

    # The intersection of the above two.
    matches = [x for x in i_swiped_right if x.swipee in they_swiped_right]

    return render(request, "matches.html", {"matches": matches})
