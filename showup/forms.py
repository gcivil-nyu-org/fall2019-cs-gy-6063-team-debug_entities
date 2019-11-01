from .models import Concert, CustomUser, Match
from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import UserChangeForm


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=255, label="First Name")
    last_name = forms.CharField(max_length=255, label="Last Name")
    date_of_birth = forms.DateField()
    gender = forms.CharField(max_length=255)
    email = forms.EmailField()

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.gender = self.cleaned_data["gender"]
        user.save()

        # Get events and users.
        events = Concert.objects.values_list("id", flat=True)
        users = CustomUser.objects.values_list("id", flat=True)

        # Add any missing info to Match.
        for uid_1 in users:
            for uid_2 in users:
                if uid_1 != uid_2 and uid_1 < uid_2:
                    for eid in events:
                        try:
                            row = Match.objects.get(uid_1=uid_1, uid_2=uid_2, eid=eid)
                        except Match.DoesNotExist:
                            row = Match(uid_1=uid_1, uid_2=uid_2, eid=eid)
                            row.save()

        return user


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ("bio", "genres")
        widgets = {"genres": forms.CheckboxSelectMultiple}
