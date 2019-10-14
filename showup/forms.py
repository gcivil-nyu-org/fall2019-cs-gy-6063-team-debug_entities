from django import forms
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=255, label='First Name')
    last_name = forms.CharField(max_length=255, label='Last Name')
    date_of_birth = forms.DateField()
    gender = forms.CharField(max_length=255)
    email = forms.EmailField()

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.gender = self.cleaned_data['gender']
        user.email = self.cleaned_data['email']
        user.save()
        return user
