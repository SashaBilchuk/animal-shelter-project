from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dog/<int:dog_id>/', views.detail_dog, name='detail_dog'),
    path('cat/<int:cat_id>/', views.detail_cat, name='detail_cat'),
    path('add_dog_adoption/', views.add_dog_adoption, name='add_dog_adoption'),
    path('search/', views.search, name='search'),
    path('admin/logout/', views.logout, name='logout'),
    path('admin/', views.admin, name='add_animal'),
    path('admin/shelter/cat/add/', views.add_cat, name='add_cat'),
    path('admin/shelter/dog/add/', views.add_dog, name='add_dog'),
    path('reports/', views.reportURL, name='reports'),
    path('download_report/', views.download_report, name='download_report'),
    path('fetch-from-google-sheet/', views.fetch_from_sheet, name='google-sheet'),
    path('fetch_black_list_from_sheet/', views.fetch_black_list_from_sheet, name='black_list')

]
