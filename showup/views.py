from django.shortcuts import render
from .models import Concert


def home(request):
    return render(request, 'home.html')


def events(request):
    if request.user.is_authenticated:
        events = Concert.objects.all()
        borough_choices = Concert.BOROUGH_CHOICES
        
        #User clicks "Filter"
        if('filter' in request.GET):
            #filter boroughs
            if('boroughs' in request.GET):
                events = events.filter(borough__in=request.GET.getlist('boroughs'))
            
        # User clicked "Interested" button.
        if('interested' in request.GET):
            event_id = request.GET.get('interested')
            request.user.interested.add(event_id)

        # User clicked "Going" button.
        if('going' in request.GET):
            event_id = request.GET.get('going')
            request.user.going.add(event_id)

        return render(request, 'events.html', {'events': events, 'borough_choices': borough_choices})
    else:
        return render(request, 'home.html')
