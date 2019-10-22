from django.shortcuts import render
from .models import Concert
from datetime import datetime

def home(request):
    return render(request, 'home.html')

def get_performers():
    performer_names_choices = []
    for performer in Concert.objects.all().values("performer_names"):
            performer_names_choices.extend(performer["performer_names"].split(','))
            
    performer_names_choices = [name.strip(' ') for name in performer_names_choices]
    performer_names_choices = list(set(performer_names_choices))
    performer_names_choices.sort()
    return performer_names_choices
    
def get_venues():
    venue_name_choices = []
    for venue in Concert.objects.all().values("venue_name"):
            venue_name_choices.extend([venue["venue_name"]])
    venue_name_choices = [name.strip(' ') for name in venue_name_choices]
    venue_name_choices = list(set(venue_name_choices))
    venue_name_choices.sort()
    return venue_name_choices
    
def get_genres():
    genre_choices = []
    for genre in Concert.objects.all().values("genres"):
            genre_choices.extend(genre["genres"].split(', '))
            
    genre_choices = [name.strip(' ') for name in genre_choices]
    genre_choices = list(set(genre_choices))
    genre_choices.sort()
    return genre_choices
    
def events(request):
    if request.user.is_authenticated:
        events = Concert.objects.all()
        borough_choices = Concert.BOROUGH_CHOICES
        performer_names_choices = get_performers()
        venue_name_choices = get_venues()
        genre_choices = get_genres()
        start_date = end_date = datetime.today()
        
        
        #User clicks "Filter"
        if('filter' in request.GET):
            #filter boroughs
            if('boroughs' in request.GET):
                events = events.filter(borough__in=request.GET.getlist("boroughs"))
                
            #filter performers. only 1 performer at the moment
            if("performers" in request.GET):
                events = events.filter(performer_names__contains=request.GET["performers"])
                
            #filter venues
            if("venues" in request.GET):
                events = events.filter(venue_name__in=request.GET.getlist("venues"))
            
            #filter genres. only 1 genre at the moment
            if("genres" in request.GET):
                events = events.filter(genres__contains=request.GET["genres"])
            
        # User clicked "Interested" button.
        if('interested' in request.GET):
            event_id = request.GET.get('interested')
            request.user.interested.add(event_id)

        # User clicked "Going" button.
        if('going' in request.GET):
            event_id = request.GET.get('going')
            request.user.going.add(event_id)

        return render(request, 'events.html', {'events': events,
            'borough_choices': borough_choices, 'performer_names_choices': performer_names_choices,
            'venue_choices': venue_name_choices, 'genre_choices': genre_choices, 'start_date': start_date,
            'end_date': end_date})
    else:
        return render(request, 'home.html')
