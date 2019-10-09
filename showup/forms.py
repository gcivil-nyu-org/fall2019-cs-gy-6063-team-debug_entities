from django import forms
from .models import Users
from django.forms import ModelForm

class UserSignUpForm(ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = Users
		fields = ['firstName','lastName','dateOfBirth','gender','email','password']
