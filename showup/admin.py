from .models import Concert, CustomUser, Genre, Squad, Swipe
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
                    "bio",
                    "genres",
                    "squad",
                )
            },
        ),
    )
    add_fieldsets = fieldsets

    class Meta:
        model = CustomUser


class SquadAdmin(admin.ModelAdmin):
    inlines = (SwipeInline,)
    readonly_fields = ("id",)

    class Meta:
        model = Squad


class GenreAdmin(admin.ModelAdmin):
    list_display = ["genre"]

    class Meta:
        model = Genre


class SwipeAdmin(admin.ModelAdmin):
    list_display = ["swiper", "swipee", "event", "direction"]

    class Meta:
        model = Swipe


class ConcertAdmin(admin.ModelAdmin):
    class Meta:
        model = Concert


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Squad, SquadAdmin)
admin.site.register(Swipe, SwipeAdmin)
admin.site.register(Concert, ConcertAdmin)
