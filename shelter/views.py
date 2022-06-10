from .models import Dog, Cat, Adopter, Response, DogAdoption, CatAdoption, CatFostering, Foster, DogFostering, BlackList
from .forms import DogAdoptionsForm, CatAdoptionsForm, AddDog, CatFosteringForm, DogFosteringForm, BlackListForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.shortcuts import render
from itertools import chain
import datetime as dt
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
from django.urls import reverse_lazy

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


def add_cat(request):
    return redirect('admin/shelter/cat/add/')


def add_dog(request):
    if request.method == 'POST':
        form = AddDog(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddDog
    return render(request, 'add_dog.html', {'form': form})


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
    if request.method == 'POST':
        form = DogAdoptionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            dog = form.cleaned_data.get('dog')
            if dog.location == "Association" or "Pension":
                dog.exit_date = dt.date.today()
            # elif dog.location == "Foster":
                #להוסיף שגיאה שלא ניתן לעבור מאומנה ישירות לאימוץ (קודם לסגור אומנה )
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
           # if dog.location == "Adoption":
           # להוסיף שגיאה שלא ניתן לעבור מאימוץ ישירות לאומנה (קודם לסגור אימוץ )
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
                cat.exit_date = dt.date.today()
            # elif cat.location == "Foster":
            # להוסיף שגיאה שלא ניתן לעבור מאומנה ישירות לאימוץ (קודם לסגור אומנה )
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
            # if cat.location == "Adoption":
            # # להוסיף שגיאה שלא ניתן לעבור מאימוץ ישירות לאומנה (קודם לסגור אימוץ )
            cat.location = 'Foster'
            cat.save()
            foster = form.cleaned_data.get('foster')
            foster.activity_status = 'Active'
            foster.save()
            return redirect('home')
    else:
        form = CatFosteringForm

    return render(request, 'add_cat_fostering.html', {'form': form})


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
    # creds = ServiceAccountCredentials.from_json_keyfile_name('./pbpython-345313-70ce25d6b97c.json', scope)
    creds = ServiceAccountCredentials.from_json_keyfile_name('./final-project-98653-e0d93d9d971e.json', scope)

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
    grades = []
    return Nlabeled, labeled, data


def normalize_grades(cur_grade, max_all, min_all):
    return int(round((((MAXGRADE - MINGRADE) / (max_all - min_all)) * (cur_grade - max_all) + MAXGRADE), 0))


def grading_response():
    """
    takes Response from models and calculates the grade for each instance
    :return: merged dataFrame, with original data, sorted by grade (Descending) - headers still in english
    """
    start_time = time.time()
    df = pd.DataFrame(list(Response.objects.all().values()))
    Nlabeled, labeled, data = prepare_data(df)
    data_no_labels = data.drop(['y'], axis=1)
    X = data_no_labels.values[:, 1:len(data_no_labels.columns)]
    grading_vec = np.array([0,0,0,0,0,1,1,1,0.5,1,0.5,2,1,1,-15,2,1,2,-10,2,-0.2,-1])
    grades = X@grading_vec

    data_no_labels['grade'] = grades.tolist() # add grade column to df without labels

    df_aux = data_no_labels[['QID', 'grade']] # creat aux dataframe
    df_aux = df_aux.set_index('QID')
    df = df.set_index('QID')
    sorted_df = df.merge(df_aux, left_index=True, right_index=True)
    sorted_df.reset_index(inplace=True)

    # insert grade by KNN score
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

    print(f'grading response took {time.time()- start_time}')
    return sorted_df


def create_header_dict(tablename):
    if tablename == "row_up":
        map_dict = {
            'id': 'מזהה שאלון',
            'response_owner': 'מי מטפלת? ',
            'status': 'סטטוס',
            'comments': 'הערות עמותה',
            'full_name': 'שם',
            'dog_name': 'שם הכלב לפנייה',
            'age': 'גיל',
            'city': 'עיר',
            'normGrade': 'ציון מנורמל',

        }
    elif tablename == "row_expended":
        map_dict = {
        'phone_num': 'טלפון',
        'mail': 'מייל',
        'maritalStatus': 'מצב משפחתי',
        'numChildren': 'מספר ילדים',
        'otherPets': 'חיות נוספות',
        'experience': 'נסיון',
        'allergies': 'אלרגיות?',
        'own_apartment': 'דירה בבעלותו',
        'rent_agreed': 'הסכמת בעל הדירה',
        'residenceType': 'סוג מגורים',
        'fence': 'יש גדר?',
        'dogPlace': 'היכן הכלב ישהה?',
        'dogSize': 'גודל כלב רצוי',
        'response_comments': 'הערות מהשאלון',
        'response_date': 'תאריך'}

    else:
        map_dict = {
            'id': 'מזהה רשומה',
            'name': 'שם',
            'city': 'עיר',
            'phone_num': 'טלפון',
            'comments': 'הערות עמותה'
        }

    return map_dict


def add_to_Response(row):
    start_time = time.time()
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
    print(f'add to  response took {time.time()- start_time}')



def add_to_black_list(full_name,city,mail, phone_num, comments):
    BlackList.objects.create(full_name=full_name,  city=city, mail=mail, phone_num=phone_num,  comments=comments)


def update_response_model():
    start_time = time.time()
    sheet_instance = get_sheet()
    print(f'got records from google sheet, took: {time.time() - start_time}')
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)
    records_df = records_df[records_df['Timestamp'] != ""]
    records_df = convert_headers(records_df)
    # records_df['convertedTimestamp'] = pd.to_datetime(records_df['Timestamp']).astype(np.int32)
    records_df['convertedTimestamp'] = pd.to_datetime(records_df['Timestamp'])
    records_df['convertedTimestamp'] = records_df['convertedTimestamp'].dt.strftime("%m/%d/%Y, %H:%M:%S")
    # records_df = records_df.assign(QID=lambda x: ((x['convertedTimestamp']) + (x['age'])))
    records_df = records_df.assign(QID=lambda x: (x['convertedTimestamp']))
    records_df['QID'] = records_df.QID.apply(str)

    # records_df = records_df[records_df['QID'][0] != '0']
    context = {
        'df': records_df
    }
    QID_list = list(Response.objects.values_list('QID', flat=True))
    Response_status_dict = dict(Response.objects.all().values_list("QID", "status"))
    Response_phone_dict = dict(Response.objects.all().values_list("QID", "phone_num"))
    black_list_phones = list(BlackList.objects.values_list('phone_num', flat=True))

    # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
    for index, row in records_df.iterrows():
        # response_model = Response.objects.values_list('QID', flat=True)
        # black_list_phones = BlackList.objects.values_list('phone_num', flat=True)
        cur_QID = str(row['QID'])

        if cur_QID not in QID_list:
            QID_list.append(cur_QID)
            add_to_Response(row)
            cur_phone = "0" + str(row['phone_num'])
            # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
            if str(cur_phone) not in black_list_phones and (row['status'] == 'רשימה שחורה'):
                black_list_phones.append(cur_phone)
                full_name = row['full_name']
                city = row['city']
                phone_num = "0" + str(row['phone_num'])
                mail = row['mail']
                comments = row['comments']
                add_to_black_list(full_name,city, mail, phone_num, comments)

        else:
            if Response_phone_dict[cur_QID] not in black_list_phones and Response_status_dict[cur_QID] == 'רשימה שחורה':
                response = Response.objects.get(QID = cur_QID)
                black_list_phones.append(response.phone_num)
                # black_df = pd.DataFrame.from_records(response.to_dict())
                full_name = response.full_name
                city = response.city
                mail = response.mail
                phone_num = response.phone_num
                comments = response.comments
                add_to_black_list(full_name, city, mail, phone_num, comments)
                response.save()

            # response_owner_row = row['response_owner']
            # status_row = row['status']
            # comments_row = row['comments']
            # response.response_owner = response_owner_row
            # response.status = status_row
            # response.comments = comments_row
    print(f"still in update response, took total of: {time.time() - start_time}")

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
    records_df = pd.DataFrame(list(BlackList.objects.all().values()))
    records_df = records_df.drop(['mail'], axis=1)
    records_df = records_df.sort_values('full_name', ascending=True)
    headers = create_header_dict("blacklist")
    context = {
        'df': records_df,
        'headers': headers
    }
    return render(request, 'black_list.html', context)


def get_test_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('./pbpython-345313-70ce25d6b97c.json', scope)
    creds = ServiceAccountCredentials.from_json_keyfile_name('./final-project-98653-e0d93d9d971e.json', scope)

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

    # def get_success_url(self):
    #     pk = self.kwargs["pk"]
    #     return reverse("view-employer", kwargs={"pk": pk})
    # redirect('recommendation')
