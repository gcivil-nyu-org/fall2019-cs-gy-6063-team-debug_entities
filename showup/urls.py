from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events',views.events, name='events'),
    path('accounts/', include('allauth.urls')),
    url(r'^user/', views.events, name='events'),
]
