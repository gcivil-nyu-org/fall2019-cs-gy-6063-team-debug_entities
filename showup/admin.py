from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


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
                )
            },
        ),
    )
    add_fieldsets = fieldsets

    class Meta:
        model = CustomUser


admin.site.register(CustomUser, CustomUserAdmin)
