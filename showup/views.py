from django.shortcuts import render
from .models import Concert


def home(request):
    return render(request, 'home.html')


def events(request):
    if request.user.is_authenticated:
        events = Concert.objects.all()
        return render(request, 'events.html', {'events': events})
    else:
        return render(request, 'home.html')
