from django.core.management.base import BaseCommand
from showup.models import CustomUser
from allauth.account.admin import EmailAddress


class Command(BaseCommand):
    def handle(self, *args, **options):
        password = "heyhey123"
        name = "Vik"
        email = "vm1564@nyu.edu"

        new_superuser = CustomUser.objects.create_superuser(  # make superuser
            username=name, email=email, password=password, first_name=name
        )
        print()
        EmailAddress.objects.get_or_create(  # verify superuser's email
            user=new_superuser, email=email, verified=True
        )
        print(f"I made {name} as a superuser and verified {email}")

        for i in range(1, 10):
            email = f"vm1564+{i}@nyu.edu"
            name = f"Vik{i}"
            new_user = CustomUser.objects.create_user(  # make normal users
                username=name, email=email, password=password, first_name=name
            )
            EmailAddress.objects.get_or_create(  # verify their emails
                user=new_user, email=email, verified=True
            )
            print(f"I made {name} as a normal user and verified {email}")
