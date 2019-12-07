from .models import CustomUser, Squad
from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import UserChangeForm
from datetime import datetime
from django.core.exceptions import ValidationError


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=255, label="First Name")
    last_name = forms.CharField(max_length=255, label="Last Name")
    date_of_birth = forms.DateField()
    gender = forms.CharField(max_length=255)
    email = forms.EmailField()

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data["date_of_birth"]
        if date_of_birth is not None and date_of_birth > datetime.today().date():
            raise ValidationError("Please enter a valid date of birth")
        return date_of_birth

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.gender = self.cleaned_data["gender"]
        squad = Squad.objects.create()
        squad.save()
        user.squad = squad
        user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ("bio", "genres")
        widgets = {"genres": forms.CheckboxSelectMultiple}


class SquadForm(forms.Form):
    email = forms.EmailField(required=False)


class CustomUserForm(UserChangeForm):
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data["date_of_birth"]
        if date_of_birth is not None and date_of_birth > datetime.today().date():
            raise ValidationError("Please enter a valid date of birth")
        return date_of_birth

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "date_of_birth", "gender")

    def save(self, request):
        user = super(CustomUserForm, self).save(request)
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.gender = self.cleaned_data["gender"]
        user.save()
        return user
