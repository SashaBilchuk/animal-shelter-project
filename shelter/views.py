from .models import Dog, Cat, Adopter, Response, DogAdoption, CatAdoption, CatFostering, Foster, DogFostering, BlackList
from .forms import DogAdoptionsForm, CatAdoptionsForm, AddDog, AddCat, AddAdopter, AddFoster, CatFosteringForm,\
                DogFosteringForm, BlackListForm, DogAdoptionsEdit, DogFosteringEdit, CatAdoptionsEdit, CatFosteringEdit
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.shortcuts import render
from itertools import chain
from datetime import datetime as dt
import datetime
from django.views.generic import ListView
from django.http import HttpRequest
from django.core import serializers
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import sklearn
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from django.views.generic import UpdateView
from django.http import HttpResponseRedirect, HttpResponse
import numpy as np
from sklearn.model_selection import train_test_split
import time

from .algo_func import KNN, prepare_data, normalize_grades, get_black_list, get_sheet, grading_response,\
    create_header_dict, add_to_Response,update_response_model, add_to_black_list, convert_headers, get_test_sheet, add_to_adopter, convert_ascii_sum

# from .forms import AddToSheet

def home(request):
    cats = Cat.objects.filter(
        Q(location__icontains='Association')
        | Q(location__icontains='Foster')
        | Q(location__icontains='Pension'))
    cats = cats.order_by('location')

    cat_count = 0
    for cat in cats:
        if cat.location == 'Association' or 'Foster' or 'Pension':
            cat_count += 1
    no_of_cats = cat_count

    paginator1 = Paginator(cats, 8)
    page1 = request.GET.get('catpage')
    cats = paginator1.get_page(page1)

    dogs = Dog.objects.filter(
        Q(location__icontains='Association')
        | Q(location__icontains='Foster')
        | Q(location__icontains='Pension'))
    dogs = dogs.order_by('location')

    dog_count = 0
    for dog in dogs:
        if dog.location == 'Association' or 'Foster' or 'Pension':
            dog_count += 1
    no_of_dogs = dog_count

    paginator2 = Paginator(dogs, 8)
    page2 = request.GET.get('dogpage')
    dogs = paginator2.get_page(page2)

    no_of_animals = no_of_cats + no_of_dogs
    return render(request, 'home.html', {'cats': cats,
                                         'dogs': dogs,
                                         'no_of_animals': no_of_animals,
                                         'no_of_dogs': no_of_dogs,
                                         'no_of_cats': no_of_cats})


def all_cats(request):
    return render(request, 'all_cats.html', {'cats': Cat.objects.order_by('acceptance_date').all(), 'cat_adoption': CatAdoption.objects.all(),
                                             'cat_fostering': CatFostering.objects.all()})


def all_dogs(request):
    return render(request, 'all_dogs.html', {'dogs': Dog.objects.order_by('acceptance_date').all(), 'dog_adoption': DogAdoption.objects.all(),
                                             'dog_fostering': DogFostering.objects.all()})


def detail_cat(request, cat_id):
    cat = get_object_or_404(Cat, pk=cat_id)
    if cat.location == "Adoption":
        return render(request, 'detail_cat.html', {'cat': cat, 'cat_adoption': CatAdoption.objects.get(cat=cat.id)})
    elif cat.location == "Foster":
        return render(request, 'detail_cat.html', {'cat': cat, 'cat_fostering': CatFostering.objects.get(cat=cat.id)})
    return render(request, 'detail_cat.html', {'cat': cat})


def detail_dog(request, dog_id):
    dog = get_object_or_404(Dog, pk=dog_id)
    if dog.location == "Adoption":
        return render(request, 'detail_dog.html', {'dog': dog, 'dog_adoption': DogAdoption.objects.get(dog=dog.id)})
    elif dog.location == "Foster":
        return render(request, 'detail_dog.html', {'dog': dog, 'dog_fostering': DogFostering.objects.get(dog=dog.id)})
    return render(request, 'detail_dog.html', {'dog': dog})


def search(request):
    dogs = Dog.objects.all()
    cats = Cat.objects.all()

    search_query = request.GET.get('q')

    if search_query:
        cats = cats.filter(
            Q(name__icontains=search_query) |
            Q(animal_type__icontains=search_query) |
            Q(adopter_relation_cat__adopter_city__icontains=search_query)
        )
        dogs = dogs.filter(
            Q(name__icontains=search_query) |
            Q(chip_number__iexact=search_query) |
            Q(animal_type__icontains=search_query) |
            Q(adopter_relation_dog__adopter_city__icontains=search_query)
        )

    results = chain(dogs, cats)
    return render(request, 'search.html', {'shelter': list(results), 'search_query': search_query})


def admin(request):
    return redirect('/admin')


def add_dog(request):
    if request.method == 'POST':
        form = AddDog(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddDog
    return render(request, 'add_dog.html', {'form': form})


def add_cat(request):
    if request.method == 'POST':
        form = AddCat(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddCat
    return render(request, 'add_cat.html', {'form': form})


def add_adopter(request):
    if request.method == 'POST':
        form = AddAdopter(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddAdopter
    return render(request, 'add_adopter.html', {'form': form})


def add_foster(request):
    if request.method == 'POST':
        form = AddFoster(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddFoster
    return render(request, 'add_foster.html', {'form': form})


def edit_dog(request, dog_id):
    dog = Dog.objects.get(id=dog_id)
    if request.method == 'POST':
        form = AddDog(request.POST, request.FILES, instance=dog)
        if form.is_valid():
            form.save()
            return redirect('detail_dog', dog.id)
    else:
        form = AddDog(instance=dog)
    return render(request, 'edit_dog.html', {'form': form})


def edit_cat(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    if request.method == 'POST':
        form = AddCat(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('detail_cat', cat.id)
    else:
        form = AddCat(instance=cat)
    return render(request, 'edit_cat.html', {'form': form})


def edit_adopter(request, adopter_id):
    adopter = Adopter.objects.get(id=adopter_id)
    if request.method == 'POST':
        form = AddAdopter(request.POST, request.FILES, instance=adopter)
        if form.is_valid():
            form.save()
            return redirect('report_adopters')
    else:
        form = AddAdopter(instance=adopter)
    return render(request, 'edit_adopter.html', {'form': form})


def edit_foster(request, foster_id):
    foster = Foster.objects.get(id=foster_id)
    if request.method == 'POST':
        form = AddFoster(request.POST, request.FILES, instance=foster)
        if form.is_valid():
            form.save()
            return redirect('report_fosters')
    else:
        form = AddFoster(instance=foster)
    return render(request, 'edit_foster.html', {'form': form})


def logout(request):
    return redirect('admin/logout/')


def add_to_black_list_form(request):
    list = BlackList.objects.all()
    if request.method == 'POST':
        form = BlackListForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = BlackListForm

    return render(request, 'add_to_black_list.html', {'black_list': list, 'form': form})


def add_dog_adoption(request):
    if request.method == 'POST':
        form = DogAdoptionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            dog = form.cleaned_data.get('dog')
            if dog.location == "Association" or "Pension":
                dog.exit_date = form.cleaned_data.get('adoption_date')
                dog.save()
            dog.location = 'Adoption'
            dog.save()
            adopter = form.cleaned_data.get('adopter')
            adopter.activity_status = 'Adopted'
            adopter.save()
            return redirect('home')
    else:
        form = DogAdoptionsForm

    return render(request, 'add_dog_adoption.html', {'form': form})


def add_dog_fostering(request):
    if request.method == 'POST':
        form = DogFosteringForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            dog = form.cleaned_data.get('dog')
            dog.location = 'Foster'
            dog.save()
            foster = form.cleaned_data.get('foster')
            foster.activity_status = 'Active'
            foster.save()
            return redirect('home')
    else:
        form = DogFosteringForm

    return render(request, 'add_dog_fostering.html', {'form': form})


def add_cat_adoption(request):
    if request.method == 'POST':
        form = CatAdoptionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cat = form.cleaned_data.get('cat')
            if cat.location == "Association" or "Pension":
                cat.exit_date = form.cleaned_data.get('adoption_date')
                cat.save()
            cat.location = 'Adoption'
            cat.save()
            adopter = form.cleaned_data.get('adopter')
            adopter.activity_status = 'Adopted'
            adopter.save()
            return redirect('home')
    else:
        form = CatAdoptionsForm

    return render(request, 'add_cat_adoption.html', {'form': form})


def add_cat_fostering(request):
    if request.method == 'POST':
        form = CatFosteringForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cat = form.cleaned_data.get('cat')
            cat.location = 'Foster'
            cat.save()
            foster = form.cleaned_data.get('foster')
            foster.activity_status = 'Active'
            foster.save()
            return redirect('home')
    else:
        form = CatFosteringForm

    return render(request, 'add_cat_fostering.html', {'form': form})


def edit_dog_adoption(request, dogadoption_id):
    dogadoption = DogAdoption.objects.get(id=dogadoption_id)
    if request.method == 'POST':
        form = DogAdoptionsEdit(request.POST, request.FILES, instance=dogadoption)
        if form.is_valid():
            form.save()
            if dogadoption.return_date:
                dogadoption.dog.location = 'Association'
                dogadoption.dog.acceptance_date = dogadoption.return_date
                dogadoption.dog.save()
                dogadoption.adopter.activity_status = 'Returned'
                dogadoption.adopter.save()
            return redirect('report_dog_adoptions')
    else:
        form = DogAdoptionsEdit(instance=dogadoption)
    return render(request, 'edit_dog_adoption.html', {'form': form})


def edit_cat_adoption(request, catadoption_id):
    catadoption = CatAdoption.objects.get(id=catadoption_id)
    if request.method == 'POST':
        form = CatAdoptionsEdit(request.POST, request.FILES, instance=catadoption)
        if form.is_valid():
            form.save()
            if catadoption.return_date:
                catadoption.cat.location = 'Association'
                catadoption.cat.acceptance_date = catadoption.return_date
                catadoption.cat.save()
                catadoption.adopter.activity_status = 'Returned'
                catadoption.adopter.save()
            return redirect('report_cat_adoptions')
    else:
        form = CatAdoptionsEdit(instance=catadoption)
    return render(request, 'edit_cat_adoption.html', {'form': form})


def edit_dog_fostering(request, dogfostering_id):
    dogfostering = DogFostering.objects.get(id=dogfostering_id)
    if request.method == 'POST':
        form = DogFosteringEdit(request.POST, request.FILES, instance=dogfostering)
        if form.is_valid():
            form.save()
            if dogfostering.fostering_date_end:
                dogfostering.dog.location = 'Association'
                dogfostering.dog.save()
            return redirect('report_dog_fostering')
    else:
        form = DogFosteringEdit(instance=dogfostering)
    return render(request, 'edit_dog_fostering.html', {'form': form})


def edit_cat_fostering(request, catfostering_id):
    catfostering = CatFostering.objects.get(id=catfostering_id)
    if request.method == 'POST':
        form = CatFosteringEdit(request.POST, request.FILES, instance=catfostering)
        if form.is_valid():
            form.save()
            if catfostering.fostering_date_end:
                catfostering.cat.location = 'Association'
                catfostering.cat.save()
            return redirect('report_cat_fostering')
    else:
        form = CatFosteringEdit(instance=catfostering)
    return render(request, 'edit_cat_fostering.html', {'form': form})


def report_adopters(request):
    return render(request, "report_adopters.html", {'adopters': Adopter.objects.order_by('activity_status').all()})


def report_fosters(request):
    return render(request, "report_fosters.html", {'fosters': Foster.objects.order_by('activity_status').all()})


def report_dog_adoptions(request):
    return render(request, "report_dog_adoptions.html", {'dogs': DogAdoption.objects.order_by('adoption_date').all()})


def report_cat_adoptions(request):
    return render(request, "report_cat_adoptions.html", {'cats': CatAdoption.objects.order_by('adoption_date').all()})


def report_dog_fostering(request):
    return render(request, "report_dog_fostering.html", {'dogs': DogFostering.objects.order_by('fostering_date_start').all()})


def report_cat_fostering(request):
    return render(request, "report_cat_fostering.html", {'cats': CatFostering.objects.order_by('fostering_date_start').all()})



############################################# Responses ############################################################

def get_recommendation(request):
    header_up_row = create_header_dict("row_up")
    headers_expended = create_header_dict("row_expended")
    if len(list(Response.objects.all().values())):
        results = grading_response()
        results.response_date = results.response_date.apply(lambda x: x.date())
        results = results[['id', 'response_owner', 'status', 'comments', 'full_name', 'dog_name', 'age',
       'city', 'normGrade', 'phone_num', 'mail', 'maritalStatus', 'numChildren',
       'otherPets', 'experience',  'allergies', 'own_apartment',
       'rent_agreed', 'residenceType', 'fence', 'dogPlace', 'dogSize',
       'response_comments', 'response_date']]
        not_handled = results.query("status in ('','טרם טופל')") # filter by dates
        not_handled = not_handled[not_handled.response_date > dt.today().date() - pd.to_timedelta("15day")]

        initial_contact = results.query("status in ('בוצעה שיחה ראשונית', 'ממתינים לוידאו')")
        initial_contact = initial_contact[initial_contact.response_date > dt.today().date() - pd.to_timedelta("30day")]

        adoption_approved = results.query("status in ('מאושר לאימוץ')")


        context = {
            'not_handled': not_handled,
            'initial_contact': initial_contact,
            'adoption_approved': adoption_approved,
            'header_up_row': header_up_row,
            'headers_expended': headers_expended
        }
    else:
        context = {

            'header_up_row': header_up_row
        }

    if (request.GET.get('mybtn')):
        start_time = time.time()
        update_response_model()
        print(f'all updation took{time.time() -start_time } secs')
        return HttpResponseRedirect('/recommendation_system')

    return render(request, 'Recommender.html', context)


def fetch_black_list_from_sheet(request):
    records_df = pd.DataFrame(list(BlackList.objects.all().values()))
    records_df = records_df.drop(['mail'], axis=1)
    records_df = records_df.sort_values('full_name', ascending=True)
    headers = create_header_dict("blacklist")
    context = {
        'df': records_df,
        'headers': headers
    }
    return render(request, 'black_list.html', context)


def fetch_from_sheet(request):
    sheet_instance = get_sheet()
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)
    records_df = records_df[records_df['Timestamp'] != ""]
    records_df = convert_headers(records_df)
    records_df['convertedTimestamp'] = pd.to_datetime(records_df['Timestamp'])
    records_df['convertedTimestamp'] = records_df['convertedTimestamp'].dt.strftime("%m/%d/%Y, %H:%M:%S")
    records_df = records_df.assign(QID=lambda x: (x['convertedTimestamp']))
    records_df['QID'] = records_df.QID.apply(str)
    context = {
        'df': records_df
    }
    response_model = Response.objects.values_list('QID', flat=True)
    # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
    for index, row in records_df.iterrows():
        if row['QID'] not in response_model:
            add_to_Response(row)
    return render(request, 'google-sheet-date.html', context)


def add_to_sheet(request):
    if request.POST:
        '''
        validate posted data. then create a dataframe I give you a example below.
        '''
        form = AddToSheet(request.POST)
        if form.is_valid():
            new_df = pd.DataFrame(data={'מי מטפלת?': ['אנה']})
            sheet_instance = get_test_sheet()
            sheet_instance.append_rows(new_df.values.tolist())  # it will save the data to your sheet.
            return redirect('google-sheet')  # redirect anywhere as you want.

    return redirect('google-sheet')  # else request is not POST request


class UpdateResponseView(UpdateView):
    model = Response
    template_name = 'edit_response.html'
    fields = ['response_owner', 'status', 'comments']
    success_url = '/recommendation_system/'


class UpdateBlackList(UpdateView):
    model = BlackList
    template_name = 'edit_black_list.html'
    fields = ['full_name', 'city', 'mail', 'phone_num', 'comments']
    success_url = '/fetch_black_list_from_sheet/'
