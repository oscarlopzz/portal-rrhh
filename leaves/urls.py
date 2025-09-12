from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='leaves_home'),
    path('mis/', views.my_leaves, name='my_leaves'),
    path('mis/exportar/', views.my_leaves_export_csv, name='my_leaves_export_csv'),
    path('nueva/', views.create_leave, name='create_leave'),

    path('revisar/', views.review_list, name='leaves_review_list'),
    path('revisar/exportar/', views.review_export_csv, name='leaves_review_export_csv'),
    path('<int:pk>/revisar/', views.review_detail, name='leaves_review_detail'),
    path('mis/exportar-xlsx/', views.my_leaves_export_xlsx, name='my_leaves_export_xlsx'),
path('revisar/exportar-xlsx/', views.review_export_xlsx, name='leaves_review_export_xlsx')


]
