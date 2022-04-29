from django.shortcuts import render
from .models import Dog, Cat, Adopter, DogAdoption
from .forms import DogAdoptionsForm
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


def add_dog_adoption(request):
    dogs = Dog.objects.all()
    adopters = Adopter.objects.all()
    if request.method == 'POST':
        form = DogAdoptionsForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'home.html')
    else:
        form_class = DogAdoptionsForm

    return render(request, 'add_dog_adoption.html', {'dogs': dogs, 'adopters': adopters, 'form': form_class})


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
    # records_df = records_df.fillna(-5)
    # records_df = records_df[records_df['Timestamp'] != -5]
    records_df.dropna(
        axis=0,
        how='any',
        thresh=20,
        subset=None,
        inplace=True
    )
    # records_df = records_df[[
    #     'מי מטפלת?', 'סטטוס', 'הערות ', 'שם מלא', 'עיר מגורים', 'מייל', 'טלפון ליצירת קשר',
        # 'במידה ואתם מתעניינים בכלב מסויים אצלנו, נא ציינו את שמו']]  # If you want all columns then remove this line.
    context = {
        'df': records_df
    }
    return render(request, 'google-sheet-date.html', context)


def prepare_data(df):
    df = df.fillna(-5)
    rslt_df = df[df['Timestamp'] != -5]
    subset = rslt_df[['סטטוס', 'Timestamp', 'האם לאחד מבני המשפחה יש אלרגיה לכלבים ? ', 'ניסיון קודם בגידול כלבים: '
        , 'גיל', 'עיר מגורים', 'האם אתם מעוניינים בגודל מסוים של כלב?'
        , 'סוג מקום מגורים ', 'היכן הכלב ישהה? ', 'מצב משפחתי'
        , 'מספר ילדים', 'האם אתם מגדלים בע"ח נוסף כיום?']]

    subset = subset.rename(columns={"סטטוס": 'status',
                                    'עיר מגורים': 'City',
                                    'האם לאחד מבני המשפחה יש אלרגיה לכלבים ? ': 'Allergies',
                                    'ניסיון קודם בגידול כלבים: ': 'Experience',
                                    'גיל': 'Age',
                                    'עיר מגורים': 'City',
                                    'האם אתם מעוניינים בגודל מסוים של כלב?': 'DogSize',
                                    'סוג מקום מגורים ': 'ResidenceType',
                                    'היכן הכלב ישהה? ': 'DogPlace',
                                    'מצב משפחתי': 'MaritalStatus',
                                    'מספר ילדים': 'NumChildren',
                                    'האם אתם מגדלים בע"ח נוסף כיום?': 'OtherPets'})  # correct colum's names

    subset = subset.astype({'Age': int, 'NumChildren': int})
    subset['Small'] = np.where(subset['DogSize'].str.contains("קטן", case=False), 1, 0)
    subset['Medium'] = np.where(subset['DogSize'].str.contains("בינוני", case=False), 1, 0)
    subset['Large'] = np.where(subset['DogSize'].str.contains("גדול", case=False), 1, 0)
    subset['HasCat'] = np.where(subset['OtherPets'].str.contains("חתול", case=False), 1, 0)
    subset['HasDog'] = np.where(subset['OtherPets'].str.contains("כלב", case=False), 1, 0)
    subset['Single'] = np.where(subset['MaritalStatus'].str.contains("רווק/ה", case=False), 1, 0)
    subset['Widow'] = np.where(subset['MaritalStatus'].str.contains("אלמן/ה", case=False), 1, 0)
    subset['Married'] = np.where(subset['MaritalStatus'].str.contains("נשוי/ה", case=False), 1, 0)
    subset['Divorced'] = np.where(subset['MaritalStatus'].str.contains("גרוש/ה", case=False), 1, 0)
    subset['HomeYard'] = np.where(subset['ResidenceType'].str.contains("בית", case=False), 1, 0)
    subset['Apartment'] = np.where(subset['ResidenceType'].str.contains("דירה", case=False), 1, 0)
    subset['Dog_inside'] = np.where(subset['DogPlace'].str.contains("בית בלבד", case=False), 1, 0)
    subset['Dog_outside'] = np.where(subset['DogPlace'].str.contains("מחוץ לבית בלבד", case=False), 1, 0)
    subset['Dog_inside_outside'] = np.where(subset['DogPlace'].str.contains("בית ומחוץ לבית", case=False), 1, 0)
    subset['HasExperience'] = np.where(subset['Experience'].str.contains("יש", case=False), 1, 0)
    subset['HasAllergies'] = np.where(subset['Allergies'].str.contains("כן", case=False), 1, 0)
    subset['CityNumber'] = subset['City'].apply(lambda row: convert_ascii_sum(row))

    conditions = [
        (subset['status'] == 'אימץ מהעמותה'),
        (subset['status'] == 'מאושר לאימוץ'),
        (subset['status'] == 'בוצעה שיחה ראשונית'),
        (subset['status'] == 'ממתינים לוידאו'),
        (subset['status'] == 'טרם טופל'),
        (subset['status'] == 'לא מתאים לאימוץ'),
        (subset['status'] == 'רשימה שחורה'),
    ]

    values = [1, 1, -1, -1, -1, 0, 0]
    subset['y'] = np.select(conditions, values, default=-1)
    data = subset[['Small', 'Medium', 'Large', 'HasCat', 'HasDog', 'Single', 'Widow', 'Married', 'Divorced', 'HomeYard',
                   'Apartment',
                   'Dog_inside', 'Dog_outside', 'Dog_inside_outside', 'HasExperience', 'HasAllergies', 'CityNumber',
                   'y']]
    Nlabeled = data[data['y'] < 0]
    labeled = data[data['y'] >= 0]

    return Nlabeled, labeled, data


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


