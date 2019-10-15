from django.shortcuts import render
from .models import Concert

def home(request):
    return render(request, 'home.html')

def events(request):
    events = Concert.objects.all()
    return render(request,'events.html',{'events' : events})