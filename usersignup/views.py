from django.shortcuts import render
from .forms import UserSignUpForm
from .models import UserSignup
from .models import LoginUser

# Create your views here.
from django.http import HttpResponse

def signup(request):
	if(request.method == 'POST'):
		form = UserSignUpForm(request.POST)
		if form.is_valid():
			form.save()
	else:
		form = UserSignUpForm()
	return render(request, 'signup.html',{'form' : form})