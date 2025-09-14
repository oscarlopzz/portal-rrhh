from django.urls import path
from . import views

urlpatterns = [
    path('', views.performance_home, name='performance_home'),  # <- índice
    path('mias/', views.my_evaluations, name='my_evaluations'),
    path('revisar/', views.review_list, name='performance_review_list'),
    path('nueva/', views.create, name='performance_create'),
    path('<int:pk>/revisar/', views.review_detail, name='performance_review_detail'),
]
