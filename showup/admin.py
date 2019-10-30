from .models import CustomUser, Genre, Match
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ["email", "username", "date_of_birth", "gender"]
    readonly_fields = ("id",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "gender",
                    "email",
                    "password",
                    "bio",
                )
            },
        ),
    )
    add_fieldsets = fieldsets

    class Meta:
        model = CustomUser


class GenreAdmin(admin.ModelAdmin):
    list_display = ["genre"]

    class Meta:
        model = Genre


class MatchAdmin(admin.ModelAdmin):
    list_display = ["uid_1", "uid_2", "eid", "decision_1", "decision_2", "decision"]

    class Meta:
        model = Match


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Match, MatchAdmin)
