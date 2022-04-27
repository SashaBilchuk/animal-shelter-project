from django.shortcuts import render
from .models import Dog, Cat
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.shortcuts import render
from itertools import chain
from django.views.generic import ListView
import csv
from django.http import HttpResponse
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


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



def download_report(request):
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


def reportURL(request):
    return render(request, 'reports.html')


def list_history(request):
    header = 'דו"חות מצבת'
    queryset = Dog.objects.all().order_by('_name')
    form = ShelterHistorySearchForm(request.POST or None)
    context = {
        "header": header,
        "queryset": queryset,
        "form": form,
    }
    if request.method == 'POST':
        name = form['name'].value()
        queryset = StockHistory.objects.filter(
            item_name__icontains=form['item_name'].value(),
            last_updated__range=[
                form['start_date'].value(),
                form['end_date'].value()
            ]
        )

        if (name != ''):
            queryset = queryset.filter(name=name)

        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Dogs History.csv"'
            writer = csv.writer(response)
            writer.writerow(
                ['NAME',
                 'CHIP NUM',
                 'AGE',
                 'DAYS_IN_ASOCC'])
            instance = queryset
            for dog in instance:
                writer.writerow(
                    [dog.name,
                     dog.chip_number,
                     dog.age_years,
                     dog.days_in_the_association])
            return response

        context = {
            "form": form,
            "header": header,
            "queryset": queryset,
        }
    return render(request, "list_history.html", context)


############################################# Responses ############################################################
def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('./pbpython-345313-70ce25d6b97c.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('שאלון מועמדות לאימוץ (Responses)')
    sheet_instance = sheet.get_worksheet(0)
    return sheet_instance


def get_black_list(df):
    df = df.fillna(-5)
    rslt_df = df[df['Timestamp'] != -5]
    subset = rslt_df[rslt_df['סטטוס'] == 'רשימה שחורה'][['שם מלא', 'טלפון ליצירת קשר', 'הערות ']]
    subset = subset.fillna("-")
    subset.drop_duplicates(subset='טלפון ליצירת קשר', keep=False,inplace=True)
    subset = subset.sort_values('שם מלא', ascending=True)

    return subset[['שם מלא','טלפון ליצירת קשר','הערות ']]


def fetch_from_sheet(request):
    sheet_instance = get_sheet()
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)  # this is Panda dataframe if you need you can use it.
    records_df = records_df.fillna(-5)
    records_df = records_df[records_df['Timestamp'] != -5]
    # records_df = records_df[[
    #     'מי מטפלת?', 'סטטוס', 'הערות ', 'שם מלא', 'עיר מגורים', 'מייל', 'טלפון ליצירת קשר',
        # 'במידה ואתם מתעניינים בכלב מסויים אצלנו, נא ציינו את שמו']]  # If you want all columns then remove this line.
    context = {
        'df': records_df
    }
    return render(request, 'google-sheet-date.html', context)

def fetch_black_list_from_sheet(request):
    sheet_instance = get_sheet()
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)  # this is Panda dataframe if you need you can use it.
    records_df = get_black_list(records_df)
    context = {
        'df': records_df
    }
    return render(request, 'black_list.html', context)


def add_to_sheet(request):
    if request.POST:
        '''
        validate posted data. then create a dataframe I give you a example below.
        '''

        new_df = pd.DataFrame(data={'column_name1': ['value'], 'column_name2': ['value'],
                                    '....so on..': ''})  # example dataframe to insert in google sheet.
        sheet_instance = get_sheet()
        sheet_instance.append_rows(new_df.values.tolist())  # it will save the data to your sheet.
        return redirect('google-sheet')  # redirect anywhere as you want.

    return redirect('google-sheet')  # else request is not POST request