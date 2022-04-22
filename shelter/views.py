from django.shortcuts import render
from .models import Dog, Cat
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from itertools import chain
from django.views.generic import ListView
import csv
from django.http import HttpResponse
import datetime


def home(request):

    cats = Cat.objects.all()
    cat_count = 0
    for cat in cats:
        if cat.location == 'Association':
            cat_count += 1
    no_of_cats = cat_count

    paginator1 = Paginator(cats, 3)
    page = request.GET.get('catpage')
    cats = paginator1.get_page(page)

    dogs = Dog.objects.all()
    dog_count = 0
    for dog in dogs:
        if dog.location == 'Association':
            dog_count += 1
    no_of_dogs = dog_count

    paginator2 = Paginator(dogs, 3)
    page = request.GET.get('dogpage')
    dogs = paginator2.get_page(page)

    no_of_animals = no_of_cats + no_of_dogs
    return render(request, 'home.html', {'cats': cats,
                                         'dogs': dogs,
                                         'no_of_animals': no_of_animals,
                                         'no_of_dogs': no_of_dogs,
                                         'no_of_cats': no_of_cats})


def detail_cat(request, cat_id):
    cat = get_object_or_404(Cat, pk=cat_id)
    cats = Cat.objects.all()
    return render(request, 'detail_cat.html', {'cat': cat, 'cats': cats})


def detail_dog(request, dog_id):
    dog = get_object_or_404(Dog, pk=dog_id)
    dogs = Dog.objects.all()
    return render(request, 'detail_dog.html', {'dog': dog, 'dogs': dogs})


def search(request):
    dogs = Dog.objects.all()
    cats = Cat.objects.all()

    search_query = request.GET.get('q')

    if search_query:
        cats = cats.filter(
            Q(name__icontains=search_query) |
            Q(gender__iexact=search_query)
        )
        dogs = dogs.filter(
            Q(name__icontains=search_query) |
            Q(gender__iexact=search_query) |
            Q(chip_number__iexact=search_query)
        )

    results = chain(dogs, cats)

    return render(request, 'search.html', {'shelter': results, 'search_query': search_query})


def admin(request):
    return redirect('/admin')


def add_cat(request):
    return redirect('admin/shelter/cat/add/')


def add_dog(request):
    return redirect('admin/shelter/dog/add/')


def logout(request):
    return redirect('admin/logout/')


def Reports(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')

    writer = csv.writer(response)
    writer.writerow(['מין', 'מספר שבב', 'שם', ',תאריך לידה'])

    for dog in Dog.objects.all().values_list('gender', 'chip_number', 'name', 'birth_date'):
        dog_lst = list(dog)
        for i, val in enumerate(dog_lst):
            if val == "Male":
                dog_lst[i] = 'זכר'
            elif val == 'Female':
                dog_lst[i] = 'נקבה'
        dog = tuple(dog_lst)
        writer.writerow(dog)

    response['Content-Disposition'] = 'attachment; filename="dogs.csv"'
    return response
