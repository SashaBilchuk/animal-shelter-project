from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dog/<int:dog_id>/', views.detail_dog, name='detail_dog'),
    path('cat/<int:cat_id>/', views.detail_cat, name='detail_cat'),
    path('search/', views.search, name='search'),
    path('admin/', views.admin, name='add_animal'),
    path('admin/shelter/cat/add/', views.add_cat, name='add_cat'),
    path('admin/shelter/dog/add/', views.add_dog, name='add_dog')
]
