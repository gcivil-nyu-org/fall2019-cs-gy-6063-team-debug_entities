from django.core.management.base import BaseCommand
from showup.models import CustomUser, Squad
from allauth.account.admin import EmailAddress


class Command(BaseCommand):
    def make_user(name, email, superuser):
        # superuser is a bool telling us if the user we make should be super or not
        if CustomUser.objects.filter(email=email).exists():
            print(f"We already have a user with the email address {email}")
        else:
            squad = Squad.objects.create()
            squad.save()
            password = "heyhey123"
            if superuser:
                new_user = CustomUser.objects.create_superuser(
                    username=name,
                    email=email,
                    password=password,
                    first_name=name,
                    squad=squad,
                )
            else:
                new_user = CustomUser.objects.create_user(
                    username=name,
                    email=email,
                    password=password,
                    first_name=name,
                    squad=squad,
                )
            EmailAddress.objects.get_or_create(  # verify the user's email
                user=new_user, email=email, verified=True
            )

            print(
                f"I made {name} as a {'super' if superuser else 'normal '}user"
                f" and verified {email}"
            )

    def handle(self, *args, **options):
        superusers = [{"name": "Vik", "email": "vm1564@nyu.edu"}]
        for u in superusers:
            Command.make_user(u["name"], u["email"], True)

        normal_users = [
            {"name": f"Vik{i}", "email": f"vm1564+{i}@nyu.edu"} for i in range(1, 10)
        ]
        normal_users += [
            {"name": "Professor", "email": "gcivil@nyu.edu"},
            {"name": "Dan", "email": "dgopstein@nyu.edu"},
        ]

        for u in normal_users:
            Command.make_user(u["name"], u["email"], False)
