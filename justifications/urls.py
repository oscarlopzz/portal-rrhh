from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='justifications_home'),
    path('mios/', views.my_justifications, name='my_justifications'),
    path('nuevo/', views.create_justification, name='create_justification'),
    path('revisar/', views.review_list, name='review_list'),
    path('<int:pk>/revisar/', views.review_detail, name='review_detail'),
     path('revisar/exportar/', views.review_export_csv, name='review_export_csv'),   # ← NUEVA
]
