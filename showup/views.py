from django.shortcuts import render
from .models import Concert
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "home.html")


@login_required
def events(request):
    events = Concert.objects.all()

    # User clicked "Interested" button.
    if "interested" in request.GET:
        event_id = request.GET.get("interested")
        request.user.interested.add(event_id)

    # User clicked "Going" button.
    if "going" in request.GET:
        event_id = request.GET.get("going")
        request.user.going.add(event_id)

    return render(request, "events.html", {"events": events})


@login_required
def user(request, id):
    return render(request, "user.html")
