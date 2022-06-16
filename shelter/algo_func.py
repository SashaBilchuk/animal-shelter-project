from .models import Dog, Cat, Adopter, Response, DogAdoption, CatAdoption, CatFostering, Foster, DogFostering, BlackList
from django.shortcuts import get_object_or_404, redirect
from itertools import chain
import datetime
from datetime import datetime as dt
from django.core import serializers
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import sklearn
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from django.http import HttpResponseRedirect, HttpResponse
import numpy as np
from sklearn.model_selection import train_test_split
import time

MAXGRADE = 5
MINGRADE = 1

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
    subset['HasExperience'] = np.where(subset['experience'].str.contains("יש", case=False), 1, 0)
    subset['HasAllergies'] = np.where(subset['allergies'].str.contains("כן", case=False), 1, 0)
    # subset['CityNumber'] = subset['city'].apply(lambda row: convert_ascii_sum(row))
    subset['specificRequest'] = np.where(subset['dog_name'].apply(lambda x: x == ''), 0, 1)
    subset['HasComments'] = np.where(subset['response_comments'].apply(lambda x: x == ''), 0, 1)
    subset['own_apartment'] = np.where(subset['own_apartment'].str.contains("כן", case=False), 1, 0)
    subset['rent_agreed'] = np.where(subset['rent_agreed'].str.contains("כן", case=False), 1, 0) #1: "כן", 0: "לא", "לא יודע" כרגע

    def conditions_rental(s):
        if (s['own_apartment'] == 1) and (s['rent_agreed'] == 0):
            return 1
        else:
            return 0

    subset['No_landlord_agree'] = subset.apply(conditions_rental, axis=1)

    def conditions_divorced(s):
        if (s['Divorced'] == 1) and (s['numChildren'] >= 3) and (s['age'] >= 55):
            return 1
        else:
            return 0

    subset['Divorced3Children'] = subset.apply(conditions_divorced, axis=1)

    def conditions_Fence(s):
        if (s['HomeYard'] == 1) and (s['fence'] == 'לא'):
            return 1
        else:
            return 0
    subset['Missing_fence'] = subset.apply(conditions_Fence, axis=1)


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

    avg_age = subset[subset['y'] == 1].age.mean()  # average age of those who can adopt
    subset = subset.assign(newAge=lambda x: (abs(x['age'] - avg_age)))
    subset = subset.assign(numChildrenAbove5=np.maximum(subset.numChildren.values - 4, 0))
    subset = subset.assign(divorced3ChildersPlus=np.maximum(subset.numChildren.values - 4, 0))

    data = subset[['QID', 'age', 'numChildren', 'Small', 'Medium', 'Large', 'HasCat', 'HasDog', 'Single',
                   'Widow', 'Married', 'Divorced', 'HomeYard', 'Apartment',
                   'Dog_inside', 'Dog_outside', 'Dog_inside_outside', 'Missing_fence', 'HasExperience',
                   'HasAllergies', 'specificRequest', 'newAge', 'numChildrenAbove5','No_landlord_agree', 'Divorced3Children', 'HasComments', 'y']]


    data = data.reindex(columns=['QID', 'age', 'numChildren', 'Small', 'Medium', 'Large','Single',
                   'Widow', 'Married', 'Divorced', 'HomeYard', 'Apartment', 'HasCat', 'HasDog',
                   'Dog_inside', 'Dog_outside', 'Dog_inside_outside', 'Missing_fence', 'HasExperience',
                   'HasAllergies', 'specificRequest', 'newAge', 'numChildrenAbove5','No_landlord_agree', 'Divorced3Children', 'HasComments', 'y'])

    labeled = data[data['y'] >= 0]

    return labeled, data


def normalize_grades(cur_grade, max_all, min_all):
    return int(round((((MAXGRADE - MINGRADE) / (max_all - min_all)) * (cur_grade - max_all) + MAXGRADE), 0))


def get_black_list(df):
    df = df.fillna(-5)
    rslt_df = df[df['Timestamp'] != -5]
    subset = rslt_df[rslt_df['סטטוס'] == 'רשימה שחורה'][['שם מלא', 'טלפון ליצירת קשר', 'הערות']]
    subset = subset.fillna("-")
    subset.drop_duplicates(subset='טלפון ליצירת קשר', keep=False, inplace=True)
    subset = subset.sort_values('שם מלא', ascending=True)

    return subset[['שם מלא', 'טלפון ליצירת קשר', 'הערות']]

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('./pbpython-345313-70ce25d6b97c.json', scope)
    creds = ServiceAccountCredentials.from_json_keyfile_name('./final-project-98653-e0d93d9d971e.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('שאלון מועמדות לאימוץ (Responses)')
    sheet_instance = sheet.get_worksheet(0)
    return sheet_instance


def grading_response():
    """
    takes Response from models and calculates the grade for each instance
    :return: merged dataFrame, with original data, sorted by grade (Descending) - headers still in english
    """
    start_time = time.time()
    df = pd.DataFrame(list(Response.objects.all().values()))
    labeled, data = prepare_data(df)
    data_no_labels = data.drop(['y'], axis=1)
    X = data_no_labels.values[:, 1:len(data_no_labels.columns)]


    """
    __Not graded:________
    __parameter__ || __grade__
    age                0
    numChildren        0
    Small              0
    Medium             0
    Single             0
    Widow              0
    Married            0
    Divorced           0
    HomeYard           0
    Apartment          0
    __Graded:___________
    HasCat             1
    HasDog             1
    Dog_inside         1
    Dog_outside       -5
    Dog_inside_outside 2
    Missing_fence     -2.5
    HasExperience      5
    HasAllergies      -5
    specificRequest    2
    newAge            -0.2
    numChildrenAbove5 -1.5
    No_landlord_agree  -2
    Divorced3Children  -2
    HasComments        0.5
    """
    grading_vec = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, -5, 2, -2.5, 5, -5, 2, -0.2, -1.5, -2, -2, 0.5])

    grades = X@grading_vec


    data_no_labels['grade'] = grades.tolist() # add grade column to df without labels

    df_aux = data_no_labels[['QID', 'grade']] # creat aux dataframe
    df_aux = df_aux.set_index('QID')
    df = df.set_index('QID')
    sorted_df = df.merge(df_aux, left_index=True, right_index=True)
    sorted_df.reset_index(inplace=True)

    # insert grade by KNN score
    start_knn = time.time()
    KNN_dict = KNN(labeled, data)
    end_knn = time.time()

    for index, row in sorted_df.iterrows():
        sorted_df.loc[index, 'grade'] += KNN_dict[row['QID']] *5

    print(f'fininshed updating results after KNN, took  {time.time() - end_knn} sec')

    max_all =sorted_df['grade'].max()
    min_all = sorted_df['grade'].min()
    sorted_df = sorted_df.set_index('QID')
    sorted_df['normGrade'] = sorted_df['grade'].apply(lambda cur_grade: normalize_grades(cur_grade, max_all, min_all))


    phones_not_for_adoption = []
    not_for_adoption = Response.objects.filter(status='לא מתאים לאימוץ')
    for item in not_for_adoption:
        number = item.phone_num
        phones_not_for_adoption.append(number)
        sorted_df.loc[sorted_df['phone_num'] == number, ['grade']] = sorted_df[sorted_df['phone_num'] == number]['grade'] - 10
        sorted_df.loc[sorted_df['phone_num'] == number, ['normGrade']] = 1 #grading manually 1 star for black list
        #add case of same name or email as in black_list+ add warning on page

    # Get new black list
    black_list_phones = list(BlackList.objects.values_list('phone_num', flat=True))
    black_list_names = list(BlackList.objects.values_list('full_name', flat=True))
    black_list_mail = list(BlackList.objects.values_list('mail', flat=True))

    def conditions_not_in_black_list(s):
        if (s['phone_num'] not in black_list_phones) and (s['status'] == 'רשימה שחורה'):
            return 1
        elif (s['full_name'] in black_list_names) or (s['mail'] in black_list_mail):
            return 2
        else:
            return 0

    sorted_df['black_list_aux'] = sorted_df.apply(conditions_not_in_black_list, axis=1)
    new_black_list_df = sorted_df[sorted_df['black_list_aux'] == 1]
    if len(new_black_list_df):
        print(new_black_list_df)
        for index, row in new_black_list_df.iterrows():
            if ("0" + str(row.phone_num)) not in black_list_phones:
                full_name = row['full_name']
                city = row['city']
                phone_num = "0" + str(row['phone_num'])
                mail = row['mail']
                comments = row['comments']
                add_to_black_list(full_name, city, mail, phone_num, comments)


    for number in black_list_phones:
        sorted_df.loc[sorted_df['phone_num'] == number, ['grade']] = sorted_df[sorted_df['phone_num'] == number]['grade'] - 20
        sorted_df.loc[sorted_df['phone_num'] == number, ['normGrade']] = 0


    """below might be not relevant"""
    sorted_df['phone_num'] = sorted_df['phone_num'].apply(lambda row: str(row).zfill(10) if (len(str(row)) == 9) else (str(row).zfill(9)))

    # remove from recommendation
    # sorted_df = sorted_df[sorted_df['allergies'] == 'לא']
    # sorted_df = sorted_df[sorted_df['dogPlace'] != 'מחוץ לבית בלבד']
    idx = sorted_df[sorted_df['allergies'] == 'לא']
    sorted_df['dog_name'] = sorted_df['dog_name'].str.strip()

    sorted_df['dog_name'] = np.where(sorted_df['dog_name'].apply(lambda x: x == ''), "תשובה חסרה", sorted_df['dog_name'])
    sorted_df = sorted_df.sort_values(["dog_name", "grade"], ascending=[True, False])

    ###upon debugging--> get all records +gradings in csv
    # printable = sorted_df[['status','grade', 'normGrade']]
    # conditions = [
    #     (printable['status'] == 'אימץ מהעמותה'),
    #     (printable['status'] == 'מאושר לאימוץ'),
    #     (printable['status'] == 'בוצעה שיחה ראשונית'),
    #     (printable['status'] == 'ממתינים לוידאו'),
    #     (printable['status'] == 'טרם טופל'),
    #     (printable['status'] == 'לא מתאים לאימוץ'),
    #     (printable['status'] == 'רשימה שחורה'),
    #     (printable['status'] == ''),
    # ]
    #
    # values = [1, 1, -1, -1, -1, 2, 0, -1]
    #
    # printable['y'] = np.select(conditions, values, default=-1)
    # printable =  printable[['y', 'grade', 'normGrade']]
    # printable.to_csv('printable.csv')
    #
    # sorted_df = sorted_df.drop(['black_list_aux'], axis=1)
    sorted_df = sorted_df.drop(sorted_df[sorted_df.normGrade == 0].index)
    print(f'grading response took {time.time()- start_time}')
    return sorted_df


def create_header_dict(tablename):
    if tablename == "row_up":
        map_dict = {
            'id': 'עריכת שאלון',
            'response_owner': 'מי מטפלת? ',
            'status': 'סטטוס',
            'response_date': 'תאריך',
            'comments': 'הערות עמותה',
            'full_name': 'שם',
            'dog_name': 'כלב רצוי',
            'age': 'גיל',
            'city': 'עיר',
            'normGrade': 'ציון',

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
        'response_comments': 'הערות מהשאלון'}

    elif tablename == "raw_data_header":
        map_dict = {
            'response_owner': 'מי מטפלת? ',
            'status': 'סטטוס',
            'comments': 'הערות עמותה',
            'full_name': 'שם',
            'dog_name': 'כלב רצוי',
            'age': 'גיל',
            'city': 'עיר',
            'Timestamp': 'תאריך'
        }

    elif tablename == "raw_data_expended":
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
        'response_comments': 'הערות מהשאלון'}

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
    records_df['convertedTimestamp'] = pd.to_datetime(records_df['Timestamp'])
    records_df['convertedTimestamp'] = records_df['convertedTimestamp'].dt.strftime("%m/%d/%Y, %H:%M:%S")
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
        cur_QID = str(row['QID'])

        if cur_QID not in QID_list:
            QID_list.append(cur_QID)
            add_to_Response(row)
            cur_phone = "0" + str(row['phone_num'])
            print("phone from dataframe: ", row['phone_num'])
            print("phone after adding 0: ", cur_phone)
            # ITERATES ON ALL RAWS, IF FOUND NEW ROW -> ADD TO RESPONSE MODEL
            if str(cur_phone) not in black_list_phones and (row['status'] == 'רשימה שחורה'):
                black_list_phones.append(cur_phone)
                full_name = row['full_name']
                city = row['city']
                phone_num = "0" + str(row['phone_num'])
                mail = row['mail']
                comments = row['comments']
                add_to_black_list(full_name,city, mail, phone_num, comments)

    print(f"still in update response, took total of: {time.time() - start_time}")

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


def get_test_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('./pbpython-345313-70ce25d6b97c.json', scope)
    creds = ServiceAccountCredentials.from_json_keyfile_name('./final-project-98653-e0d93d9d971e.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('test sheet')
    sheet_instance = sheet.get_worksheet(0)
    return sheet_instance


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

