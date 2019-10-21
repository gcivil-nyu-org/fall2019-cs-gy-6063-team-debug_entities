from .forms import CustomUserChangeForm
from .models import Concert
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, reverse


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
    if request.user.is_authenticated:
        return render(request, 'user.html')
    else:
        return render(request, 'home.html')


def edit_profile(request, id):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('user', kwargs={'id': id}))
    else:
        form = CustomUserChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'edit_profile.html', args)
