from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='performance_home'),
]
