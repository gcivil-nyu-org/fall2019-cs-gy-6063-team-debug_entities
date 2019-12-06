from .forms import CustomUserForm
from .models import Concert, CustomUser, Genre, Request, Squad, Swipe
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class ConcertAdmin(admin.ModelAdmin):
    class Meta:
        model = Concert


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
        add_form = CustomUserForm


class GenreAdmin(admin.ModelAdmin):
    list_display = ["genre"]

    class Meta:
        model = Genre


class RequestAdmin(admin.ModelAdmin):
    list_display = ["requester", "requestee"]

    class Meta:
        model = Request


class SwipeInline(admin.TabularInline):
    model = Swipe
    fk_name = "swiper"


class RequestInline(admin.TabularInline):
    model = Request
    fk_name = "requester"


class SquadAdmin(admin.ModelAdmin):
    inlines = (SwipeInline, RequestInline)
    readonly_fields = ("id",)

    class Meta:
        model = Squad


class SwipeAdmin(admin.ModelAdmin):
    list_display = ["swiper", "swipee", "event", "direction"]

    class Meta:
        model = Swipe


admin.site.register(Concert, ConcertAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Squad, SquadAdmin)
admin.site.register(Swipe, SwipeAdmin)
