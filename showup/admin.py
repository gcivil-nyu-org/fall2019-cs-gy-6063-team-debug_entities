from .models import CustomUser, Genre
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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Genre, GenreAdmin)
