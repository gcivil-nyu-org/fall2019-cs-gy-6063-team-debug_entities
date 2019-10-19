from django.shortcuts import render, redirect
from .models import Concert, CustomUser
from .forms import CustomUserChangeForm


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


def edit_profile(request, id):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return render(request, 'user.html')

    else: 
        form = CustomUserChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'edit_profile.html',args)
