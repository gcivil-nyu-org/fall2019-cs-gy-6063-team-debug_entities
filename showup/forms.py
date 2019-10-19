from django import forms
from .models import CustomUser
from allauth.account.forms import SignupForm
from django.contrib.auth.forms import UserChangeForm


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=255, label='First Name')
    last_name = forms.CharField(max_length=255, label='Last Name')
    date_of_birth = forms.DateField()
    gender = forms.CharField(max_length=255)
    email = forms.EmailField()

    def save(self, request):
        user = super(CustomSignupForm, self).save(request) # this saves the built-in fields (first name, last name, email, password)
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.gender = self.cleaned_data['gender']
        user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email','bio','password')