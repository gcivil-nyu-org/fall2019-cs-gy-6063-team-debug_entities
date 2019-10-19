from django.shortcuts import render
from .models import Concert


def home(request):
    return render(request, 'home.html')


def events(request):
    if request.user.is_authenticated:
        events = Concert.objects.all()
        borough_choices = Concert.BOROUGH_CHOICES
        borough_selected = borough_choices
        
        #User clicks "Filter"
        if('filter' in request.GET):
            borough_selected =  request.GET.get('borough_all')
            events = Concert.objects.filter(borough__in=borough_selected)
        
        # User clicked "Interested" button.
        if('interested' in request.GET):
            event_id = request.GET.get('interested')
            request.user.interested.add(event_id)

        # User clicked "Going" button.
        if('going' in request.GET):
            event_id = request.GET.get('going')
            request.user.going.add(event_id)

        return render(request, 'events.html', {'events': events, 'borough_choices': borough_choices, 'outputtext' : borough_selected})
    else:
        return render(request, 'home.html')
