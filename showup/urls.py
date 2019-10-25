from . import views
from django.urls import path, include


urlpatterns = [
    path("", views.home, name="home"),
    path("events", views.events, name="events"),
    path("accounts/", include("allauth.urls")),
    path("u/<int:id>", views.user, name="user"),
    path("u/<int:id>/edit", views.edit_profile, name="edit_profile"),
]