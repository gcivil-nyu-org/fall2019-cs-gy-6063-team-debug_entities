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
            {"name": "Muhammad", "email": "mma525@nyu.edu"},
            {"name": "Alex", "email": "ab7289@nyu.edu"},
            {"name": "Garima", "email": "gc2505@nyu.edu"},
            {"name": "Daisy", "email": "dbc291@nyu.edu"},
            {"name": "David", "email": "de846@nyu.edu"},
            {"name": "Suraj", "email": "sgg339@nyu.edu"},
            {"name": "Ayushi", "email": "ag7335@nyu.edu"},
            {"name": "Abdullah", "email": "ah4896@nyu.edu"},
            {"name": "Yixin", "email": "yh3244@nyu.edu"},
            {"name": "Xinchi", "email": "xh1255@nyu.edu"},
            {"name": "Rajeev", "email": "rri223@nyu.edu"},
            {"name": "Yonguk", "email": "yj1679@nyu.edu"},
            {"name": "Chuhan", "email": "cj1436@nyu.edu"},
            {"name": "Snehal", "email": "svk304@nyu.edu"},
            {"name": "Muhammad", "email": "mok232@nyu.edu"},
            {"name": "Michael", "email": "mfl340@nyu.edu"},
            {"name": "Patryk", "email": "pp2224@nyu.edu"},
            {"name": "Utkarsh", "email": "up293@nyu.edu"},
            {"name": "Shaurya", "email": "ss12933@nyu.edu"},
            {"name": "Abhishek", "email": "as10686@nyu.edu"},
            {"name": "Jeff", "email": "yfs219@nyu.edu"},
            {"name": "Varsha", "email": "vs2165@nyu.edu"},
            {"name": "Tara", "email": "tt1894@nyu.edu"},
            {"name": "Bhaskar", "email": "bv640@nyu.edu"},
            {"name": "Jack", "email": "jx692@nyu.edu"},
        ]

        for u in normal_users:
            Command.make_user(u["name"], u["email"], False)
