from django.shortcuts import render

from .models import Concert

# Create your views here.

def events(request):
    events = Concert.objects.all()[:8]
    return render(request,'events.html',{'events' : events})
