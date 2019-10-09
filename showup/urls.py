from django.urls import path
from . import views

app_name = "showup"

urlpatterns = [
    path('',views.events, name='event'),
]
