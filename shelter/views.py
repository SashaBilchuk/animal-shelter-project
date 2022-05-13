from django.shortcuts import render
from .models import Dog, Cat, Adopter, Response

from .forms import DogAdoptionsForm,  CatAdoptionsForm, DogDeathForm

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.shortcuts import render
from itertools import chain
from django.views.generic import ListView
import csv
from django.http import HttpResponse
from django.core import serializers
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import sklearn
from sklearn.neighbors import KNeighborsClassifier
from django.http import HttpResponseRedirect
# from .forms import AddToSheet


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
            Q(animal_type__icontains=search_query)|
            Q(adopter_relation_cat__adopter_city__icontains=search_query)
        )
        dogs = dogs.filter(
            Q(name__icontains=search_query) |
            Q(chip_number__iexact=search_query)|
            Q(animal_type__icontains=search_query)|
            Q(adopter_relation_dog__adopter_city__icontains=search_query)
        )

    results = chain(dogs, cats)
    return render(request, 'search.html', {'shelter': list(results), 'search_query': search_query})



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
        form = DogAdoptionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DogAdoptionsForm

    return render(request, 'add_dog_adoption.html', {'dogs': dogs, 'adopters': adopters, 'form': form})


def add_cat_adoption(request):
    cats = Cat.objects.all()
    adopters = Adopter.objects.all()
    if request.method == 'POST':
        form = CatAdoptionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CatAdoptionsForm

    return render(request, 'add_cat_adoption.html', {'cats': cats, 'adopters': adopters, 'form': form})


# def reportURL(request):
#     dog_data = serializers.serialize("python", Dog.objects.all())
#     cat_data = serializers.serialize("python", Cat.objects.all())
#     context = {'dog_data': dog_data, 'cat_data': cat_data}
#     return render(request, 'reports.html', context)


def add_cat_adoption(request):
    cats = Cat.objects.all()
    adopters = Adopter.objects.all()
    if request.method == 'POST':
        form = CatAdoptionsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form_class = CatAdoptionsForm

    return render(request, 'add_cat_adoption.html', {'cats': cats, 'adopters': adopters, 'form': form_class})


def reportURL(request):
    from django.core import serializers
    dog_data = serializers.serialize("python", Dog.objects.all())
    cat_data = serializers.serialize("python", Cat.objects.all())
    context = {'dog_data': dog_data, 'cat_data': cat_data}
    return render(request, 'reports.html', context)


def download_report(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="merkava.csv"'

    writer = csv.writer(response)
    writer.writerow(['ימים בעמותה', 'תאריך כניסה לעמותה', 'מספר שבב', 'סוג החיה', 'שם החיה'])
    dog_data = Dog.objects.all()
    cat_data = Cat.objects.all()

    for dog in dog_data:
        writer.writerow([dog.days_in_the_association, dog.acceptance_date, dog.chip_number, 'כלב', dog.name])
    for cat in cat_data:
        writer.writerow([cat.days_in_the_association, cat.acceptance_date, '---', 'חתול', cat.name])

    return response


def reportURL(request):
    header = 'דו"חות מצבת'
    queryset = Dog.objects.all()
    form = DogDeathForm(request.POST or None)
    context = {
        "header": header,
        "queryset": queryset,
        "form": form,
    }
    if request.method == 'POST':

        queryset = Dog.objects.filter(death_date__range=[form['death_date'].value(), form['death_date'].value()])

        context = {
            "header": header,
            "queryset": queryset,
            "form": form,
        }

        # if (name != ''):
        #     queryset = queryset.filter(name=name)
        #
        # if download_report:
        #     response = HttpResponse(content_type='text/csv')
        #     response['Content-Disposition'] = 'attachment; filename="Dogs History.csv"'
        #     writer = csv.writer(response)
        #     writer.writerow(
        #         ['NAME',
        #          'CHIP NUM',
        #          'AGE',
        #          'DAYS_IN_ASOCC'])
        #     instance = queryset
        #     for dog in instance:
        #         writer.writerow(
        #             [dog.name,
        #              dog.chip_number,
        #              dog.age_years,
        #              dog.days_in_the_association])
        #     return response

    return render(request, "reports.html", context)


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

##  old~~~~~!!!!!!!!
# def fetch_from_sheet(request):
#     sheet_instance = get_sheet()
#     records_data = sheet_instance.get_all_records()
#     records_df = pd.DataFrame.from_dict(records_data)  # this is Panda dataframe if you need you can use it.
#     # records_df = records_df.fillna(-5)
#     # records_df = records_df[records_df['Timestamp'] != -5]
#     records_df.dropna(
#         axis=0,
#         how='any',
#         thresh=20,
#         subset=None,
#         inplace=True
#     )
#     # records_df = records_df[[
#     #     'מי מטפלת?', 'סטטוס', 'הערות ', 'שם מלא', 'עיר מגורים', 'מייל', 'טלפון ליצירת קשר',
#         # 'במידה ואתם מתעניינים בכלב מסויים אצלנו, נא ציינו את שמו']]  # If you want all columns then remove this line.
#     context = {
#         'df': records_df
#     }
#     return render(request, 'google-sheet-date.html', context)
##  old~~~~~!!!!!!!!


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


def convert_headers(df):
    subset = df[['מי מטפלת?', 'סטטוס','הערות', 'Timestamp',  'שם מלא',  'גיל','עיר מגורים', 'טלפון ליצירת קשר',
                      'מייל',  'מצב משפחתי', 'מספר ילדים', 'האם אתם מגדלים בע"ח נוסף כיום?', 'ניסיון קודם בגידול כלבים: ',
                      'במידה ואתם מתעניינים בכלב מסויים אצלנו, נא ציינו את שמו',
                      'האם לאחד מבני המשפחה יש אלרגיה לכלבים ? ','האם הדירה בבעלותכם? ',
                      'במידה ואתם גרים בשכירות - האם יש הסכמת בעל הדירה?',
                      'סוג מקום מגורים ',
                      'במידה וישנה חצר, האם היא מגודרת?',
                      'היכן הכלב ישהה? ',
                      'האם אתם מעוניינים בגודל מסוים של כלב?','הערות נוספות ', 'מזהה שאלון']]

    subset = subset.rename(columns={'מי מטפלת?': 'response_owner',
                                    'סטטוס': 'status',
                                     'הערות': 'comments',
                                    'שם מלא':'full_name',
                                     'גיל': 'age',
                                     'עיר מגורים': 'city',
                                     'טלפון ליצירת קשר':'phone_num',
                                     'מייל':'mail',
                                     'מצב משפחתי': 'maritalStatus',
                                     'מספר ילדים': 'numChildren',
                                     'האם אתם מגדלים בע"ח נוסף כיום?': 'otherPets',
                                     'ניסיון קודם בגידול כלבים: ': 'experience',
                                     'במידה ואתם מתעניינים בכלב מסויים אצלנו, נא ציינו את שמו': 'dog_name',
                                     'האם לאחד מבני המשפחה יש אלרגיה לכלבים ? ': 'allergies',
                                     'האם הדירה בבעלותכם? ':'own_apartment',
                                     'במידה ואתם גרים בשכירות - האם יש הסכמת בעל הדירה?': 'rent_agreed',
                                     'סוג מקום מגורים ': 'residenceType',
                                    'במידה וישנה חצר, האם היא מגודרת?':'fence',
                                     'היכן הכלב ישהה? ': 'dogPlace',
                                     'האם אתם מעוניינים בגודל מסוים של כלב?': 'dogSize',
                                     'הערות נוספות ': 'response_comments',
                                    'מזהה שאלון': 'QID',
                                    })  # correct colum's names

    subset['age'] = subset[['age']].astype('int')
    subset['QID'] = subset['QID'].astype('int')
    subset['numChildren'] = subset['numChildren'].astype('int')

    return subset


def fetch_black_list_from_sheet(request):
    sheet_instance = get_sheet()
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)  # this is Panda dataframe if you need you can use it.
    records_df = get_black_list(records_df)
    context = {
        'df': records_df
    }
    return render(request, 'black_list.html', context)

# old AAddTo Sheet
# def add_to_sheet(request):
#     if request.POST:
#         '''
#         validate posted data. then create a dataframe I give you a example below.
#         '''
#
#         new_df = pd.DataFrame(data={'column_name1': ['value'], 'column_name2': ['value'],
#                                     '....so on..': ''})  # example dataframe to insert in google sheet.
#         sheet_instance = get_sheet()
#         sheet_instance.append_rows(new_df.values.tolist())  # it will save the data to your sheet.
#         return redirect('google-sheet')  # redirect anywhere as you want.
#
#     return redirect('google-sheet')  # else request is not POST request


def get_test_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('./pbpython-345313-70ce25d6b97c.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('test sheet')
    sheet_instance = sheet.get_worksheet(0)
    return sheet_instance


def fetch_from_sheet(request):
    sheet_instance = get_sheet()
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)
    records_df['IDX'] = pd.to_datetime(records_df['Timestamp']).astype(np.int64)
    records_df = records_df[records_df['IDX'] >0 ]
    records_df = convert_headers(records_df)

    context = {
        'df': records_df
    }
    responce_model = list(Response.objects.all())
      # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
    for index, row in records_df.iterrows():
        if row['QID'] not in responce_model:
            add_to_Response(row)

    return render(request, 'google-sheet-date.html', context)

def add_to_adopter(row):
    name = row['שם מלא']
    city = row['עיר מגורים']
    phone_number = row['טלפון ליצירת קשר']
    mail = row['מייל']
    Adopter.objects.create(adopter_ID=12345, name=name, adopter_city=city, email_address=mail, phone_number=phone_number)


def convert_ascii_sum(word):#Convert city names to ascii value
    ascii_values = [ord(character) for character in word]
    number = 0
    for val in ascii_values:
        number+=val
    return number


def add_to_Response(row):
    response_owner= row['response_owner']
    status = row['status']
    comments =row['comments']
    full_name = row['full_name']
    age = row['age']
    city = row['city']
    phone_num =row['phone_num']
    mail =row['mail']
    maritalStatus =row['maritalStatus']
    numChildren = row['numChildren']
    otherPets =row['otherPets']
    experience = row['experience']
    dog_name = row['dog_name']
    allergies = row['allergies']
    own_apartment = row['own_apartment']
    rent_agreed = row['rent_agreed']
    residenceType = row['residenceType']
    fence = row['fence']
    dogPlace = row['dogPlace']
    dogSize = row['dogSize']
    response_comments = row['response_comments']
    QID = row['QID']


    Response.objects.create(response_owner=response_owner, status=status, comments= comments, full_name=full_name,
                           age=age, city=city,  phone_num=phone_num, mail=mail, maritalStatus=maritalStatus,
                           numChildren=numChildren,otherPets=otherPets, experience=experience, dog_name=dog_name,
                           allergies=allergies, own_apartment=own_apartment, rent_agreed=rent_agreed,
                           residenceType=residenceType, fence=fence, dogPlace=dogPlace,dogSize=dogSize,
                           response_comments=response_comments, QID=QID)

def add_to_sheet(request):
    if request.POST:
        '''
        validate posted data. then create a dataframe I give you a example below.
        '''
        form = AddToSheet(request.POST)
        if form.is_valid():
            print("Hi")
            new_df = pd.DataFrame(data={'מי מטפלת?': ['אנה']})
            sheet_instance = get_test_sheet()
            sheet_instance.append_rows(new_df.values.tolist())  # it will save the data to your sheet.
            return redirect('google-sheet')  # redirect anywhere as you want.

    return redirect('google-sheet')  # else request is not POST request

