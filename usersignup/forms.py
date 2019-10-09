from django import forms
from .models import UserSignup
from django.forms import ModelForm

class UserSignUpForm(ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = UserSignup
		fields = ['username','firstName','lastName','dateOfBirth','gender','email','password']