from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.home, name="home"),
    path("events", views.events, name="events"),
    path("matches", views.matches, name="matches"),
    path("accounts/", include("allauth.urls")),
    path("u/<int:id>", views.user, name="user"),
    path("u/<int:id>/edit", views.edit_profile, name="edit_profile"),
    path("s/<int:id>", views.squad, name="squad"),
    path("s/<int:id>/edit", views.edit_squad, name="edit_squad"),
    path("<int:eid>/match", views.event_stack, name="event_stack"),
    path("avatar/", include("avatar.urls")),
    path("messages/<int:squad1>-<int:squad2>", views.messages, name="messages"),
    path("requests", views.requests, name="requests")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
