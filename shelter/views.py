from django.shortcuts import render
from .models import Dog, Cat, Adopter, Response, DogAdoption, CatAdoption, CatFostering, Foster, DogFostering, BlackList
from .forms import DogAdoptionsForm, CatAdoptionsForm, DogDeathForm, CatFosteringForm, DogFosteringForm, BlackListForm
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
from sklearn.linear_model import LogisticRegression

from django.http import HttpResponseRedirect
from datetime import datetime
import numpy as np
from sklearn.model_selection import train_test_split


MAXGRADE = 5
MINGRADE = 1


# from .forms import AddToSheet


def home(request):
    cats = Cat.objects.filter(
        Q(location__icontains='Association')
        | Q(location__icontains='Foster')
        | Q(location__icontains='Pension'))
    cats = cats.order_by('location')

    cat_count = 0
    for cat in cats:
        if cat.location == 'Association' or cat.location == 'Foster' or cat.location == 'Pension':
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
        if dog.location == 'Association' or dog.location == 'Foster' or dog.location == 'Pension':
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


def detail_cat(request, cat_id):
    cat = get_object_or_404(Cat, pk=cat_id)
    if CatAdoption.objects.filter(cat=cat.id):
        return render(request, 'detail_cat.html', {'cat': cat, 'cat_adoption': CatAdoption.objects.get(cat=cat.id)})
    if CatFostering.objects.filter(cat=cat.id):
        return render(request, 'detail_cat.html', {'cat': cat, 'cat_fostering': CatFostering.objects.get(cat=cat.id)})
    return render(request, 'detail_cat.html', {'cat': cat})


def detail_dog(request, dog_id):
    dog = get_object_or_404(Dog, pk=dog_id)
    if DogAdoption.objects.filter(dog=dog.id):
        return render(request, 'detail_dog.html', {'dog': dog, 'dog_adoption': DogAdoption.objects.get(dog=dog.id)})
    if DogFostering.objects.filter(dog=dog.id):
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


def add_cat(request):
    return redirect('admin/shelter/cat/add/')


def add_dog(request):
    return redirect('admin/shelter/dog/add/')


def add_adopter(request):
    return redirect('admin/shelter/adopter/add/')


def add_foster(request):
    return redirect('admin/shelter/foster/add/')


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
    dogs = Dog.objects.all()
    adopters = Adopter.objects.all()
    if request.method == 'POST':
        form = DogAdoptionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            dog = form.cleaned_data.get('dog')
            dog.location = 'Adoption'
            dog.save()
            adopter = form.cleaned_data.get('adopter')
            adopter.activity_status = 'אימצ/ה'
            adopter.save()
            return redirect('home')
    else:
        form = DogAdoptionsForm

    return render(request, 'add_dog_adoption.html', {'dogs': dogs, 'adopters': adopters, 'form': form})


def add_dog_fostering(request):
    dogs = Dog.objects.all()
    fosters = Foster.objects.all()
    if request.method == 'POST':
        form = DogFosteringForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            dog = form.cleaned_data.get('dog')
            dog.location = 'Foster'
            dog.save()
            foster = form.cleaned_data.get('foster')
            foster.activity_status = 'פעיל עם חיה'
            foster.save()
            return redirect('home')
    else:
        form = DogFosteringForm

    return render(request, 'add_dog_fostering.html', {'dogs': dogs, 'fosters': fosters, 'form': form})


def add_cat_adoption(request):
    cats = Cat.objects.all()
    adopters = Adopter.objects.all()
    if request.method == 'POST':
        form = CatAdoptionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cat = form.cleaned_data.get('cat')
            cat.location = 'Adoption'
            cat.save()
            adopter = form.cleaned_data.get('adopter')
            adopter.activity_status = 'אימצ/ה'
            adopter.save()
            return redirect('home')
    else:
        form = CatAdoptionsForm

    return render(request, 'add_cat_adoption.html', {'cats': cats, 'adopters': adopters, 'form': form})


def add_cat_fostering(request):
    cats = Cat.objects.all()
    fosters = Foster.objects.all()
    if request.method == 'POST':
        form = CatFosteringForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cat = form.cleaned_data.get('cat')
            cat.location = 'Foster'
            cat.save()
            foster = form.cleaned_data.get('foster')
            foster.activity_status = 'פעיל עם חיה'
            foster.save()
            return redirect('home')
    else:
        form = CatFosteringForm

    return render(request, 'add_cat_fostering.html', {'cats': cats, 'fosters': fosters, 'form': form})


# def reportURL(request):
#     dog_data = serializers.serialize("python", Dog.objects.all())
#     cat_data = serializers.serialize("python", Cat.objects.all())
#     context = {'dog_data': dog_data, 'cat_data': cat_data}
#     return render(request, 'reports.html', context)


def report_adopter_URL(request):
    queryset = Adopter.objects.all()
    context = {
        "queryset": queryset,
    }

    return render(request, "reports_adopters.html", context)


def report_foster_URL(request):
    queryset = Foster.objects.all()
    context = {
        "queryset": queryset,
    }

    return render(request, "reports_fosters.html", context)


def report_adoptions_URL(request):
    querysetdogs = DogAdoption.objects.all()
    querysetcats = CatAdoption.objects.all()
    context = {
        "querysetdogs": querysetdogs,
        "querysetcats": querysetcats
    }

    return render(request, "reports_adoptions.html", context)


def report_fostering_URL(request):
    querysetdogs = DogFostering.objects.all()
    querysetcats = CatFostering.objects.all()
    context = {
        "querysetdogs": querysetdogs,
        "querysetcats": querysetcats
    }

    return render(request, "reports_fostering.html", context)


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
        queryset = Dog.objects.filter(death_date__contains=(form['death_date'].value(), form['death_date'].value()))

        context = {
            "header": header,
            "queryset": queryset,
            "form": form,
        }

    return render(request, "reports.html", context)

############################################# Responses ############################################################

def KNN(labeled, all_data):
    y = labeled['y']
    labeled = labeled.drop(['y', 'QID'], axis=1)
    model = KNeighborsClassifier(n_neighbors=3)
    data = all_data.drop(['y', 'QID'], axis=1)
    X_train = labeled
    y_train = y
    # train the sample_data
    model.fit(X_train, y=y_train)
    y_pred = model.predict(data)
    proba = model.predict_proba(data)
    res_dict = {}
    QID_list = all_data['QID'].tolist()
    for i,qid in enumerate(QID_list):
        res_dict[qid] = proba[i][1]
    return(res_dict)


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
    subset = rslt_df[rslt_df['סטטוס'] == 'רשימה שחורה'][['שם מלא', 'טלפון ליצירת קשר', 'הערות']]
    subset = subset.fillna("-")
    subset.drop_duplicates(subset='טלפון ליצירת קשר', keep=False, inplace=True)
    subset = subset.sort_values('שם מלא', ascending=True)

    return subset[['שם מלא', 'טלפון ליצירת קשר', 'הערות']]


def prepare_data(df):
    """
    :param df: data frame from models- Response
    :return: table converted to binary for recommendation system
    """
    subset = df.astype({'age': int, 'numChildren': int})
    subset['Small'] = np.where(subset['dogSize'].str.contains("קטן", case=False), 1, 0)
    subset['Medium'] = np.where(subset['dogSize'].str.contains("בינוני", case=False), 1, 0)
    subset['Large'] = np.where(subset['dogSize'].str.contains("גדול", case=False), 1, 0)
    subset['HasCat'] = np.where(subset['otherPets'].str.contains("חתול", case=False), 1, 0)
    subset['HasDog'] = np.where(subset['otherPets'].str.contains("כלב", case=False), 1, 0)
    subset['Single'] = np.where(subset['maritalStatus'].str.contains("רווק/ה", case=False), 1, 0)
    subset['Widow'] = np.where(subset['maritalStatus'].str.contains("אלמן/ה", case=False), 1, 0)
    subset['Married'] = np.where(subset['maritalStatus'].str.contains("נשוי/ה", case=False), 1, 0)
    subset['Divorced'] = np.where(subset['maritalStatus'].str.contains("גרוש/ה", case=False), 1, 0)
    subset['HomeYard'] = np.where(subset['residenceType'].str.contains("בית", case=False), 1, 0)
    subset['Apartment'] = np.where(subset['residenceType'].str.contains("דירה", case=False), 1, 0)
    subset['Dog_inside'] = np.where(subset['dogPlace'].str.contains("בית בלבד", case=False), 1, 0)
    subset['Dog_outside'] = np.where(subset['dogPlace'].str.contains("מחוץ לבית בלבד", case=False), 1, 0)
    subset['Dog_inside_outside'] = np.where(subset['dogPlace'].str.contains("בית ומחוץ לבית", case=False), 1, 0)
    subset['Has_fence'] = np.where(subset['fence'].str.contains("כן", case=False), 1,
                                   np.where(subset['fence'].str.contains("לא", case=False), -5, 0))
    subset['HasExperience'] = np.where(subset['experience'].str.contains("יש", case=False), 1, 0)
    subset['HasAllergies'] = np.where(subset['allergies'].str.contains("כן", case=False), 1, 0)
    # subset['CityNumber'] = subset['city'].apply(lambda row: convert_ascii_sum(row))
    subset['specificRequest'] = np.where(subset['dog_name'].apply(lambda x: x == ''), 0, 1)

    conditions = [
        (subset['status'] == 'אימץ מהעמותה'),
        (subset['status'] == 'מאושר לאימוץ'),
        (subset['status'] == 'בוצעה שיחה ראשונית'),
        (subset['status'] == 'ממתינים לוידאו'),
        (subset['status'] == 'טרם טופל'),
        (subset['status'] == 'לא מתאים לאימוץ'),
        (subset['status'] == 'רשימה שחורה'),
        (subset['status'] == ''),
    ]

    values = [1, 1, -1, -1, -1, 0, 0, -1]
    subset['y'] = np.select(conditions, values, default=-1)
    # new_y = subset.age.mean() #STOPPED HERE - need to update data in db (avg outlier) QID = 1643364054000006045
    avg_age = subset[subset['y'] == 1].age.mean()  # average age of those who can adopt
    # subset['newAge'] = abs(subset['age'] - avg_age)
    subset = subset.assign(newAge=lambda x: (abs(x['age'] - avg_age)))
    subset = subset.assign(numChildrenAbove5=np.maximum(subset.numChildren.values - 4, 0))

    data = subset[['QID', 'age', 'numChildren', 'Small', 'Medium', 'Large', 'HasCat', 'HasDog', 'Single',
                   'Widow', 'Married', 'Divorced', 'HomeYard', 'Apartment',
                   'Dog_inside', 'Dog_outside', 'Dog_inside_outside', 'Has_fence', 'HasExperience',
                   'HasAllergies', 'specificRequest', 'newAge', 'numChildrenAbove5', 'y']]

    data = data.reindex(columns=['QID', 'age', 'numChildren', 'Small', 'Medium', 'Large', 'HasCat', 'HasDog', 'Single',
                                 'Widow', 'Married', 'Divorced', 'HomeYard', 'Apartment',
                                 'Dog_inside', 'Dog_outside', 'Dog_inside_outside', 'Has_fence', 'HasExperience',
                                 'HasAllergies', 'specificRequest', 'newAge', 'numChildrenAbove5', 'y'])

    Nlabeled = data[data['y'] < 0]
    Nlabeled = Nlabeled[['QID', 'age', 'numChildren', 'Small', 'Medium', 'Large', 'HasCat', 'HasDog', 'Single',
                         'Widow', 'Married', 'Divorced', 'HomeYard', 'Apartment',
                         'Dog_inside', 'Dog_outside', 'Dog_inside_outside', 'Has_fence', 'HasExperience',
                         'HasAllergies', 'specificRequest', 'newAge', 'numChildrenAbove5']]

    labeled = data[data['y'] >= 0]
    # print(Nlabeled)
    grades = []
    return Nlabeled, labeled, data


def normalize_grades(cur_grade, max_all, min_all):
    return int(round((((MAXGRADE - MINGRADE) / (max_all - min_all)) * (cur_grade - max_all) + MAXGRADE), 0))


def grading_response():
    """
    takes Response from models and calculates the grade for each instance
    :return: merged dataFrame, with original data, sorted by grade (Descending) - headers still in english
    """
    df = pd.DataFrame(list(Response.objects.all().values()))
    Nlabeled, labeled, data = prepare_data(df)
    data_no_labels = data.drop(['y'], axis=1)
    X = data_no_labels.values[:, 0:len(data_no_labels.columns)]
    grading_vec = np.array([0,0,0,0,0,0,1,1,1,0.5,1,0.5,2,1,1,-15,2,1,2,-10,2,-0.2,-1])
    grades = X@grading_vec

    data_no_labels['grade'] = grades.tolist() # add grade column to df without labels

    df_aux = data_no_labels[['QID', 'grade']] # creat aux dataframe
    df_aux = df_aux.set_index('QID')
    df = df.set_index('QID')
    sorted_df = df.merge(df_aux, left_index=True, right_index=True)
    # TODO: check if can remove reset index
    sorted_df.reset_index(inplace=True)
    KNN_dict = KNN(labeled, data)


    list_grade_before_change = sorted_df['grade'].tolist()
    for key, val in KNN_dict.items():
        idx = sorted_df[sorted_df['QID'] == key].index.values
        sorted_df.loc[idx[0],['grade']] += val
    list_grade_after_change = sorted_df['grade'].tolist()

    max_all =sorted_df['grade'].max()
    min_all = sorted_df['grade'].min()
    sorted_df = sorted_df.set_index('QID')
    sorted_df['normGrade'] = sorted_df['grade'].apply(lambda cur_grade: normalize_grades(cur_grade, max_all, min_all))


    phones_not_for_adoption = []
    not_for_adoption = Response.objects.filter(status='לא מתאים לאימוץ')
    black_list = BlackList.objects.all()
    for item in not_for_adoption:
        number = item.phone_num
        phones_not_for_adoption.append(number)
        sorted_df.loc[sorted_df['phone_num'] == number,['grade']] = sorted_df[sorted_df['phone_num'] == number]['grade'] - 10
        sorted_df.loc[sorted_df['phone_num'] == number,['normGrade']] = 1


    phones_black_list = []
    for item in black_list:
        number = item.phone_num
        phones_black_list.append(number)
        sorted_df.loc[sorted_df['phone_num'] == number,['grade']] = sorted_df[sorted_df['phone_num'] == number]['grade'] - 20
        sorted_df.loc[sorted_df['phone_num'] == number,['normGrade']] = 1


    """below might be not relevant"""
    sorted_df['phone_num'] = sorted_df['phone_num'].apply(lambda row: str(row).zfill(10) if (len(str(row)) == 9) else (str(row).zfill(9)))

    # remove from recommendation
    sorted_df = sorted_df[sorted_df['allergies'] == 'לא']
    sorted_df = sorted_df[sorted_df['dogPlace'] != 'מחוץ לבית בלבד']
    idx = sorted_df[sorted_df['allergies'] == 'לא']
    sorted_df['dog_name'] = np.where(sorted_df['dog_name'].apply(lambda x: x == ''), "תשובה חסרה", sorted_df['dog_name'])
    sorted_df = sorted_df.sort_values(["dog_name", "grade"], ascending=[True, False])
    sorted_df = sorted_df.drop(['grade'], axis=1)
    # sorted_df = sorted_df.drop(['id'], axis=1)


    return sorted_df



def create_header_dict():
    map_dict = {
        'id': 'מזהה שאלון',
        'response_owner': 'מי מטפלת? ',
        'status': 'סטטוס',
        'comments':'הערות עמותה',
        'full_name': 'שם',
        'age': 'גיל',
        'city': 'עיר',
        'phone_num': 'טלפון',
        'mail': 'מייל',
        'maritalStatus': 'מצב משפחתי',
        'numChildren': 'מספר ילדים',
        'otherPets': 'חיות נוספות',
        'experience': 'נסיון',
        'dog_name': 'שם הכלב לפנייה',
        'allergies': 'אלרגיות?',
        'own_apartment': 'דירה בבעלותו',
        'rent_agreed': 'הסכמת בעל הדירה',
        'residenceType': 'סוג ממגורים',
        'fence': 'יש גדר?',
        'dogPlace': 'היכן הכלב ישהה?',
        'dogSize': 'גודל כלב רצוי',
        'response_comments': 'הערות מהשאלון',
        'response_date': 'תאריך',
        'normGrade': 'ציון מנורמל',
    }
    return map_dict



def add_to_Response(row):
    response_owner = row['response_owner']
    status = row['status']
    comments = row['comments']
    full_name = row['full_name']
    age = row['age']
    city = row['city']
    phone_num = "0" + str(row['phone_num'])
    mail = row['mail']
    maritalStatus = row['maritalStatus']
    numChildren = row['numChildren']
    otherPets = row['otherPets']
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
    response_date = pd.to_datetime(row['Timestamp'])
    QID = row['QID']

    Response.objects.create(response_owner=response_owner, status=status, comments=comments, full_name=full_name,
                            age=age, city=city, phone_num=phone_num, mail=mail, maritalStatus=maritalStatus,
                            numChildren=numChildren, otherPets=otherPets, experience=experience, dog_name=dog_name,
                            allergies=allergies, own_apartment=own_apartment, rent_agreed=rent_agreed,
                            residenceType=residenceType, fence=fence, dogPlace=dogPlace, dogSize=dogSize,
                            response_comments=response_comments, response_date=response_date, QID=QID)

def add_to_black_list(row):
    name = row['full_name']
    city = row['city']
    phone_num = "0" + str(row['phone_num'])
    mail = row['mail']
    comments = row['comments']

    BlackList.objects.create(name=name,city=city,phone_num=phone_num,email_address=mail,comments=comments)

def update_response_model():
    sheet_instance = get_sheet()
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)
    records_df = records_df[records_df['Timestamp'] != ""]
    records_df = convert_headers(records_df)
    records_df['convertedTimestamp'] = pd.to_datetime(records_df['Timestamp']).astype(np.int64)
    records_df = records_df.assign(QID=lambda x: (x['convertedTimestamp'] + x['age']))
    records_df = records_df[records_df['QID'] > 0]
    context = {
        'df': records_df
    }

    # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
    for index, row in records_df.iterrows():
        response_model = Response.objects.values_list('QID', flat=True)
        black_list_phones = BlackList.objects.values_list('phone_num', flat=True)
        cur_QID = row['QID']
        cur_phone = "0" + str(row['phone_num'])
        # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
        if str(cur_phone) not in black_list_phones and (row['status'] == 'רשימה שחורה'):
            print(cur_phone)
            add_to_black_list(row)
            print(BlackList.objects.values_list('phone_num', flat=True))
        if cur_QID not in response_model:
            add_to_Response(row)
        else:
            response_owner_row = row['response_owner']
            status_row = row['status']
            comments_row = row['comments']
            response = Response.objects.get(QID = cur_QID)
            response.response_owner = response_owner_row
            response.status = status_row
            response.comments = comments_row
            response.save()





def get_recommendation(request):
    update_response_model()
    hebrew_headers_dict = create_header_dict()
    results = grading_response()
    results.response_date = results.response_date.apply(lambda x: x.date())

    not_handled = results.query("status in ('','טרם טופל')") # filter by dates
    not_handled = not_handled[not_handled.response_date > datetime.today().date() - pd.to_timedelta("15day")]


    initial_contact = results.query("status in ('בוצעה שיחה ראשונית', 'ממתינים לוידאו')")
    initial_contact = initial_contact[initial_contact.response_date > datetime.today().date() - pd.to_timedelta("30day")]

    adoption_approved = results.query("status in ('מאושר לאימוץ')")


    context = {
        'not_handled': not_handled,
        'initial_contact': initial_contact,
        'adoption_approved': adoption_approved,
        'hebrew_headers_dict': hebrew_headers_dict
    }

    return render(request, 'Recommender.html', context)



def convert_headers(df):
    subset = df[['מי מטפלת?', 'סטטוס', 'הערות', 'Timestamp', 'שם מלא', 'גיל', 'עיר מגורים', 'טלפון ליצירת קשר',
                 'מייל', 'מצב משפחתי', 'מספר ילדים', 'האם אתם מגדלים בע"ח נוסף כיום?', 'ניסיון קודם בגידול כלבים: ',
                 'במידה ואתם מתעניינים בכלב מסוים אצלנו, אנא ציינו את שמו ב̲ל̲ב̲ד̲ כפי שפורסם ע"י העמותה',
                 'האם לאחד מבני המשפחה יש אלרגיה לכלבים ? ', 'האם הדירה בבעלותכם? ',
                 'במידה ואתם גרים בשכירות - האם יש הסכמת בעל הדירה?',
                 'סוג מקום מגורים ',
                 'במידה וישנה חצר, האם היא מגודרת?',
                 'היכן הכלב ישהה? ',
                 'האם אתם מעוניינים בגודל מסוים של כלב?', 'הערות נוספות ']]

    subset = subset.rename(columns={'מי מטפלת?': 'response_owner',
                                    'סטטוס': 'status',
                                    'הערות': 'comments',
                                    'שם מלא': 'full_name',
                                    'גיל': 'age',
                                    'עיר מגורים': 'city',
                                    'טלפון ליצירת קשר': 'phone_num',
                                    'מייל': 'mail',
                                    'מצב משפחתי': 'maritalStatus',
                                    'מספר ילדים': 'numChildren',
                                    'האם אתם מגדלים בע"ח נוסף כיום?': 'otherPets',
                                    'ניסיון קודם בגידול כלבים: ': 'experience',
                                    'במידה ואתם מתעניינים בכלב מסוים אצלנו, אנא ציינו את שמו ב̲ל̲ב̲ד̲ כפי שפורסם ע"י העמותה': 'dog_name',
                                    'האם לאחד מבני המשפחה יש אלרגיה לכלבים ? ': 'allergies',
                                    'האם הדירה בבעלותכם? ': 'own_apartment',
                                    'במידה ואתם גרים בשכירות - האם יש הסכמת בעל הדירה?': 'rent_agreed',
                                    'סוג מקום מגורים ': 'residenceType',
                                    'במידה וישנה חצר, האם היא מגודרת?': 'fence',
                                    'היכן הכלב ישהה? ': 'dogPlace',
                                    'האם אתם מעוניינים בגודל מסוים של כלב?': 'dogSize',
                                    'הערות נוספות ': 'response_comments'
                                    })  # correct colum's names

    subset['age'] = subset[['age']].astype('int')
    #    subset['QID'] = subset['QID'].astype('int')
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


def get_test_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('./pbpython-345313-70ce25d6b97c.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('test sheet')
    sheet_instance = sheet.get_worksheet(0)
    return sheet_instance


# TODO


def fetch_from_sheet(request):
    sheet_instance = get_sheet()
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)
    records_df = records_df[records_df['Timestamp'] != ""]
    records_df = convert_headers(records_df)
    records_df['convertedTimestamp'] = pd.to_datetime(records_df['Timestamp']).astype(np.int64)
    records_df = records_df.assign(QID=lambda x: (x['convertedTimestamp'] + x['age']))
    records_df = records_df[records_df['QID'] > 0]
    context = {
        'df': records_df
    }
    response_model = Response.objects.values_list('QID', flat=True)
    print(response_model)
    # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
    for index, row in records_df.iterrows():
        if row['QID'] not in response_model:
            add_to_Response(row)
    return render(request, 'google-sheet-date.html', context)




def add_to_adopter(row):
    name = row['שם מלא']
    city = row['עיר מגורים']
    phone_number = row['טלפון ליצירת קשר']
    mail = row['מייל']
    Adopter.objects.create(adopter_ID=12345, name=name, adopter_city=city, email_address=mail,
                           phone_number=phone_number)


def convert_ascii_sum(word):  # Convert city names to ascii value
    ascii_values = [ord(character) for character in word]
    number = 0
    for val in ascii_values:
        number += val
    return number



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
