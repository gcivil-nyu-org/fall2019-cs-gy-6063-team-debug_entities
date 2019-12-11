from . import views
from django.urls import path, include


urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("", views.home, name="home"),
    path("<int:eid>/match", views.event_stack, name="event_stack"),
    path("u/<int:id>", views.user, name="user"),
    path("u/<int:id>/edit", views.edit_profile, name="edit_profile"),
    path("avatar/", include("avatar.urls")),
    path("s/<int:id>", views.squad, name="squad"),
    path("s/<int:sid>/edit", views.edit_squad, name="edit_squad"),
    path("events", views.events, name="events"),
    path("matches", views.matches, name="matches"),
    path("messages/<int:squad1>-<int:squad2>", views.messages, name="messages"),
    path("requests", views.requests, name="requests"),
    path("settings", views.settings, name="settings"),
]
