from .models import CustomUser, Genre, Swipe
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class SwipeInline(admin.TabularInline):
    model = Swipe
    fk_name = "swiper"


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
                    "interested",
                    "going",
                    "bio",
                    "genres",
                )
            },
        ),
    )
    inlines = (SwipeInline,)
    add_fieldsets = fieldsets

    class Meta:
        model = CustomUser


class GenreAdmin(admin.ModelAdmin):
    list_display = ["genre"]

    class Meta:
        model = Genre


class SwipeAdmin(admin.ModelAdmin):
    list_display = ["swiper", "swipee", "event", "direction"]

    class Meta:
        model = Swipe


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Swipe, SwipeAdmin)
