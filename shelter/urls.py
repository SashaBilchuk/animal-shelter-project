from django.contrib import admin
from django.urls import path, include
from . import views
from .views import UpdateResponseView, UpdateBlackList


urlpatterns = [
    path('', views.home, name='home'),
    path('dog/<int:dog_id>/', views.detail_dog, name='detail_dog'),
    path('cat/<int:cat_id>/', views.detail_cat, name='detail_cat'),
    path('all_cats/', views.all_cats, name='all_cats'),
    path('all_dogs/', views.all_dogs, name='all_dogs'),
    path('add_dog_adoption/', views.add_dog_adoption, name='add_dog_adoption'),
    path('add_cat_adoption/', views.add_cat_adoption, name='add_cat_adoption'),
    path('add_dog_fostering/', views.add_dog_fostering, name='add_dog_fostering'),
    path('add_cat_fostering/', views.add_cat_fostering, name='add_cat_fostering'),
    path('search/', views.search, name='search'),
    path('admin/logout/', views.logout, name='logout'),
    path('admin/', views.admin, name='add_animal'),
    path('add_dog/', views.add_dog, name='add_dog'),
    path('add_cat/', views.add_cat, name='add_cat'),
    path('add_adopter/', views.add_adopter, name='add_adopter'),
    path('add_foster/', views.add_foster, name='add_foster'),
    path('dog/<int:dog_id>/edit_dog/', views.edit_dog, name='edit_dog'),
    path('cat/<int:cat_id>/edit_cat/', views.edit_cat, name='edit_cat'),
    path('adopter/<int:adopter_id>/edit_adopter/', views.edit_adopter, name='edit_adopter'),
    path('foster/<int:foster_id>/edit_foster/', views.edit_foster, name='edit_foster'),
    path('dogadoption/<int:dogadoption_id>/edit_dog_adoption/', views.edit_dog_adoption, name='edit_dog_adoption'),
    path('catadoption/<int:catadoption_id>/edit_cat_adoption/', views.edit_cat_adoption, name='edit_cat_adoption'),
    path('dogfostering/<int:dogfostering_id>/edit_dog_fostering/', views.edit_dog_fostering, name='edit_dog_fostering'),
    path('catfostering/<int:catfostering_id>/edit_cat_fostering/', views.edit_cat_fostering, name='edit_cat_fostering'),
    path('report_adopters/', views.report_adopters, name='report_adopters'),
    path('report_fosters/', views.report_fosters, name='report_fosters'),
    path('report_dog_adoptions/', views.report_dog_adoptions, name='report_dog_adoptions'),
    path('report_cat_adoptions/', views.report_cat_adoptions, name='report_cat_adoptions'),
    path('report_dog_fostering/', views.report_dog_fostering, name='report_dog_fostering'),
    path('report_cat_fostering/', views.report_cat_fostering, name='report_cat_fostering'),
    path('fetch-from-google-sheet/', views.fetch_from_sheet, name='google-sheet'),
    path('fetch_black_list_from_sheet/', views.fetch_black_list_from_sheet, name='black_list'),
    path('recommendation_system/', views.get_recommendation, name='recommendation'),
    path('add_to_black_list/', views.add_to_black_list_form, name='add_to_black_list'),
    path('edit_response/<int:pk>/', UpdateResponseView.as_view(), name='edit_response'),
    path('edit_black_list/<int:pk>/', UpdateBlackList.as_view(), name='edit_black_list')
]
