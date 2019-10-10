from django.urls import path
from django.conf.urls import url
from . import views

app_name = "showup"

urlpatterns = [
    url(r'^$', views.home),
    url('^register/', views.register),
    url('^login/', views.login),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate_account, name='activate'),
    path('events',views.events, name='event'),
]