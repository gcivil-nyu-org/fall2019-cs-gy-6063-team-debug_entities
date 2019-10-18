from django.shortcuts import render
from .models import Concert


def home(request):
    return render(request, 'home.html')


def events(request):
    if request.user.is_authenticated:
        events = Concert.objects.all()

        # User clicked "Interested" button.
        if('interested' in request.GET):
            event_id = request.GET.get('interested')
            request.user.interested.add(event_id)

        # User clicked "Going" button.
        if('going' in request.GET):
            event_id = request.GET.get('going')
            request.user.going.add(event_id)

        return render(request, 'events.html', {'events': events})
    else:
        return render(request, 'home.html')


def user(request, id):
    if request.user.is_authenticated:
        return render(request, 'user.html')
    else:
        return render(request, 'home.html')
