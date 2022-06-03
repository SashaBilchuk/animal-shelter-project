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
    path('admin/shelter/cat/add/', views.add_cat, name='add_cat'),
    path('admin/shelter/dog/add/', views.add_dog, name='add_dog'),
    path('admin/shelter/adopter/add/', views.add_adopter, name='add_adopter'),
    path('admin/shelter/foster/add/', views.add_foster, name='add_foster'),
    path('reports/', views.reportURL, name='reports'),
    path('reports_adopters/', views.report_adopter_URL, name='reports_adopters'),
    path('reports_fosters/', views.report_foster_URL, name='reports_fosters'),
    path('reports_adoptions/', views.report_adoptions_URL, name='reports_adoptions'),
    path('reports_fostering/', views.report_fostering_URL, name='reports_fostering'),
    path('reports/download_report/', views.download_report, name='download_report'),
    path('fetch-from-google-sheet/', views.fetch_from_sheet, name='google-sheet'),
    path('fetch_black_list_from_sheet/', views.fetch_black_list_from_sheet, name='black_list'),
    path('recommendation_system/', views.get_recommendation, name='recommendation'),
    path('add_to_black_list/', views.add_to_black_list_form, name='add_to_black_list'),
    path('edit_response/<int:pk>/', UpdateResponseView.as_view(), name='edit_response'),
    path('edit_black_list/<int:pk>/', UpdateBlackList.as_view(), name='edit_black_list')

]
