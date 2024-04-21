from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_repository, name='submit_repository'),
    path('results/', views.show_results, name='show_results'),
    path('success/', views.success, name='success'),
    path('show-all/', views.show_all_results, name='show_all_files'),
    path('show-all-results/', views.show_all_results, name='show_all_results'),
]
