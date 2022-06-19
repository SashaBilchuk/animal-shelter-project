from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

import datetime
import uuid
from django.utils.translation import gettext_lazy as _


def validate_id(value):
    if len(str(value)) != 9:
        raise ValidationError(_('יש להזין מספר תעודת זהות תקין בן 9 ספרות'))


GENDER_CHOICES = (
    ('Male', 'זכר'),
    ('Female', 'נקבה'),
)


SIZE_CHOICES = (
    ('Small', 'קטן'),
    ('Medium', 'בינוני'),
    ('Big', 'גדול')
)

PLACES = (
    ('Association', 'עמותה'), ('Foster', 'אומנה'), ('Adoption', 'אימוץ'), ('Pension', 'פנסיון')
)

STATUS_ADOPTER = (
    ('Adopted', 'אימצ/ה',), ('Returned', 'החזיר/ה')
     )

STATUS_FOSTER = (
    ('Active', 'פעיל עם חיה'), ('Active with no dog', 'פעיל ללא חיה'), ('Inactive', 'לא פעיל')
     )

STATUS_CHOICES = (
    ('', ''),
    ('טרם טופל', 'טרם טופל'),
    ('בוצעה שיחה ראשונית', 'בוצעה שיחה ראשונית'),
    ('ממתינים לוידאו', 'ממתינים לוידאו'),
    ('מאושר לאימוץ', 'מאושר לאימוץ'),
    ('אימץ מהעמותה', 'אימץ מהעמותה'),
    ('לא מתאים לאימוץ', 'לא מתאים לאימוץ'),
    ('רשימה שחורה', 'רשימה שחורה'),
)


def validate_chip(value):
    if len(str(value)) != 15:
        raise ValidationError(_('יש להזין מספר שבב תקין בן 15 ספרות'))


class Adopter(models.Model):
    adopter_ID = models.IntegerField(unique=True, default=None, verbose_name=_('ת"ז'), validators=[validate_id])
    name = models.CharField(max_length=255, default=None, verbose_name=_('שם המאמצ/ת'))
    ID_link = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לת"ז'))
    birth_date = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך לידה'))
    adopter_city = models.CharField(max_length=50, default=None, verbose_name=_('עיר מגורים'))
    adopter_street = models.CharField(max_length=255, blank=True, default=None, null=True, verbose_name=_('רחוב'))
    phone_number = models.CharField(max_length=12, null=True, verbose_name=_('מספר טלפון'))
    email_address = models.EmailField(max_length=254, blank=True, default=None, null=True, verbose_name=_('כתובת מייל'))
    activity_status = models.CharField(choices=STATUS_ADOPTER, default='אימצ/ה', max_length=20, verbose_name=_('סטטוס פעילות'))
    black_listed = models.BooleanField(default=False, verbose_name=_('רשימה שחורה'))
    adopter_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות'))

    def age_years(self):
        if self.birth_date is not None:
            return datetime.date.today().year - self.birth_date.year
        else:
            return 0

    def __str__(self):
        return self.name + " (" + str(self.adopter_ID) + ")"


class Foster(models.Model):
    foster_ID = models.IntegerField(unique=True, default=None, verbose_name=_('ת"ז'),validators=[validate_id])
    name = models.CharField(max_length=255, default=None, verbose_name=_('שם האומנה'))
    ID_link = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לת"ז'))
    birth_date = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך לידה'))
    foster_city = models.CharField(max_length=50, default=None, verbose_name=_('עיר מגורים'))
    foster_street = models.CharField(max_length=255, blank=True, default=None, null=True, verbose_name=_('רחוב'))
    phone_number = models.CharField(max_length=12, null=True, verbose_name=_('מספר טלפון'))
    email_address = models.EmailField(max_length=254, blank=True, default=None, null=True, verbose_name=_('כתובת מייל'))
    activity_status = models.CharField(choices=STATUS_FOSTER, default='פעיל ללא חיה', max_length=20, verbose_name=_('סטטוס פעילות'))
    foster_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות'))

    def age_years(self):
        if self.birth_date is not None:
            return datetime.date.today().year - self.birth_date.year
        else:
            return 0

    def __str__(self):
        return self.name + " (" + str(self.foster_ID) + ")"


class Dog(models.Model):
    id = models.AutoField(primary_key=True)
    chip_number = models.BigIntegerField(unique=True, blank=True, default=None, null=True, validators=[validate_chip], verbose_name=_('מספר שבב'))
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, verbose_name=_('מין'))
    acceptance_date = models.DateField(default=datetime.date.today, blank=True, null=True, verbose_name=_('תאריך קבלה לעמותה'))
    location = models.CharField(max_length=255, choices=PLACES, default='עמותה', null=True, verbose_name=_('מיקום הכלב'))
    exit_date = models.DateField(blank=True, default=None, null=True, verbose_name=_('תאריך יציאה מעמותה'))
    #image = models.ImageField(upload_to='mediaDogs/', default='media/generic_dog.png', blank=True,verbose_name=_('הוסף תמונה'))
    physical_description = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('תיאור חיצוני'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=255, blank=True, default=None, null=True, verbose_name=_('גודל'))
    color = models.CharField(max_length=255, blank=True, default=None, null=True, verbose_name=_('צבע'))
    behaviour_description = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('תיאור התנהגותי'))
    story = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיפור רקע'))
    clinic = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מרפאה וטרינרית'))
    vaccine_book = models.BooleanField(default=False, verbose_name=_('פנקס חיסונים'))
    vaccine_book_link = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('קישור לפנקס חיסונים'))
    medical_file = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('קישור לתיק רפואי'))
    worming_1 = models.DateField(blank=True, null=True, verbose_name=_('תילוע 1'))
    worming_2 = models.DateField(blank=True, null=True, verbose_name=_('תילוע 2'))
    hexagonal_vaccine = models.DateField(blank=True, null=True, verbose_name=_('חיסון משושה'))
    next_treatment_hexagonal = models.DateField(blank=True, null=True, verbose_name=_('משושה - תאריך הטיפול הבא'))
    # nonagonal_vaccine = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתושע'))
    # ocagonal_vaccine1 = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתומן 1'))
    # ocagonal_vaccine2 = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתומן 2'))
    # ocagonal_vaccine3 = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתומן 3'))
    rabies_vaccine = models.DateField(blank=True, null=True, verbose_name=_('חיסון כלבת'))
    rabies_vaccine_link = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('אישור חיסון כלבת'))
    next_treatment_rabies = models.DateField(blank=True, null=True, verbose_name=_('כלבת - תאריך החיסון הבא'))
    ticks_fleas_treatment = models.DateField(default=None, blank=True, null=True, verbose_name=_('טיפול קרציות ופרעושים'))
    next_ticks_fleas_treatment = models.DateField(blank=True, null=True, verbose_name=_('קרציות ופרעושים - תאריך הטיפול הבא'))
    sterilization = models.DateField(blank=True, null=True, verbose_name=_('סירוס/עיקור'))
    sterilization_link = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('אישור סירוס/עיקור'))
    medical_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות רפואיות'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_date = models.DateField(blank=True, null=True, verbose_name=_('תאריך הפטירה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת הפטירה'))
    adopter_relation_dog = models.ManyToManyField(Adopter, through='DogAdoption', related_name="adoptions_dog")
    foster_relation_dog = models.ManyToManyField(Foster, through='DogFostering', related_name="fostering_dog")
    animal_type = models.CharField(max_length=32, default="כלב",  editable=False)

    @property
    def age_years(self):
        if self.birth_date is not None:
            return datetime.date.today().year - self.birth_date.year
        else:
            return 0

    @property
    def age_months(self):
        if self.birth_date is not None:
            return abs(datetime.date.today().month - self.birth_date.month)
        else:
            return 0

    @property
    def days_in_the_association(self):
        if self.acceptance_date and self.location == 'Association' or 'Foster' or 'Pension':
            return (datetime.date.today() - self.acceptance_date).days
        elif self.exit_date:
            return (self.exit_date - self.acceptance_date).days

    @property
    def get_adopters(self):
        adopters = self.adopter_relation_dog.all()
        print(type(adopters))
        return adopters

    def get_city_from_adopters(self):
        adopters = self.adopter_relation_dog.all()
        city_lst = []
        for adopter in adopters:
            city_lst.append(adopter.adopter_city)
        return city_lst

    def get_fosters(self):
        fosters = self.foster_relation_dog.all()
        print(type(fosters))
        return fosters

    def get_city_from_fosters(self):
        fosters = self.foster_relation_dog.all()
        city_lst = []
        for fosterer in fosters:
            city_lst.append(fosterer.foster_city)
        return city_lst

    def __str__(self):
        return self.name + " (" + str(self.id) + ")"


class Cat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, verbose_name=_('מין'))
    acceptance_date = models.DateField(default=datetime.date.today, blank=True, null=True,
                                       verbose_name=_('תאריך כניסה לעמותה'))
    location = models.CharField(choices=PLACES, default='עמותה', null=True, max_length=20, verbose_name=_('מיקום'))
    exit_date = models.DateField(blank=True, default=None, null=True, verbose_name=_('תאריך יציאה מעמותה'))
    physical_description = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('תיאור חיצוני'))
    #image = models.ImageField(upload_to='mediaCats/', default='media/generic_cat.png', blank=True, verbose_name=_('הוסף תמונה'))
    story = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיפור רקע'))
    clinic = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מרפאה וטרינרית'))
    vaccination_book = models.BooleanField(default=False, verbose_name=_('פנקס חיסונים'))
    vaccination_book_link = models.FileField(upload_to='mediaCats/',blank=True, default=None, null=True, verbose_name=_('קישור לפנקס חיסונים'))
    square_vaccine = models.BooleanField(default=False, verbose_name=_('חיסון מרובע'))
    ticks_fleas_treatment = models.DateField(default=None, blank=True, null=True, verbose_name=_('טיפול קרציות ופרעושים'))
    next_ticks_fleas_treatment = models.DateField(blank=True, null=True, verbose_name=_('קרציות ופרעושים - תאריך הטיפול הבא'))
    sterilization = models.DateField(default=None, blank=True, null=True, verbose_name=_('סירוס/עיקור'))
    sterilization_link = models.FileField(upload_to='mediaCats/',blank=True, default=None, null=True, verbose_name=_('אישור סירוס/עיקור'))
    medical_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות רפואיות'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת הפטירה'))
    death_date = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך הפטירה'))
    adopter_relation_cat = models.ManyToManyField(Adopter, through='CatAdoption', related_name="adoptions_cat")
    foster_relation_cat = models.ManyToManyField(Foster, through='CatFostering', related_name="fostering_cat")
    animal_type = models.CharField(max_length=32, default="חתול",  editable=False)

    @property
    def age_years(self):
        if self.birth_date is not None:
            return datetime.date.today().year - self.birth_date.year
        else:
            return 0

    def age_months(self):
        if self.birth_date is not None:
            return abs(datetime.date.today().month-self.birth_date.month)
        else:
            return 0

    @property
    def days_in_the_association(self):
        if self.acceptance_date and self.location == 'Association' or 'Foster' or 'Pension':
            return (datetime.date.today() - self.acceptance_date).days
        elif self.exit_date:
            return (self.exit_date-self.acceptance_date).days

    @property
    def get_adopters(self):
        adopters = self.adopter_relation_cat.all()
        return adopters

    def get_city_from_adopters(self):
        adopters = self.adopter_relation_cat.all()
        city_lst = []
        for adopter in adopters:
            city_lst.append(adopter.adopter_city)
        return city_lst

    def get_fosters(self):
        fosters = self.foster_relation_dog.all()
        print(type(fosters))
        return fosters

    def get_city_from_fosters(self):
        fosters = self.foster_relation_dog.all()
        city_lst = []
        for fosterer in fosters:
            city_lst.append(fosterer.foster_city)
        return city_lst

    def __str__(self):
        return self.name + " (" + str(self.id) + ")"


class DogAdoption(models.Model):
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE, verbose_name=_('שם הכלב'))
    adopter = models.ForeignKey(Adopter, on_delete=models.CASCADE, verbose_name=_('שם המאמצ/ת'))
    adoption_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך האימוץ'))
    method_of_payment = models.CharField(max_length=50, blank=True, default=None, null=True, verbose_name=_('שיטת התשלום'))
    receipt_number = models.IntegerField(blank=True, default=None, null=True, verbose_name=_('מספר חשבונית'))
    adoption_form_link = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('קישור למסמך האימוץ'))
    adoption_comments = models.TextField(blank=True, default=None, null=True, verbose_name=_('הערות האימוץ'))
    last_followup_call = models.TextField(blank=True, default=None, null=True, verbose_name=_('שיחת מעקב אחרונה'))
    next_followup_call = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך שיחת מעקב הבאה'))
    adoption_volunteer = models.TextField(blank=True, default=None, null=True, verbose_name=_('גורם מטפל באימוץ'))
    returned = models.BooleanField(default=False, verbose_name=_('החזרה'))
    return_date = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך החזרה'))
    return_reason = models.TextField(blank=True, default=None, null=True, verbose_name=_('סיבת החזרה'))
    waiver_document = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('מסמך וויתור'))
    return_volunteer = models.TextField(blank=True, default=None, null=True, verbose_name=_('גורם מטפל בהחזרה'))

    def __str__(self):
        return "{}_{}".format(self.dog.__str__(), self.adopter.__str__())


class DogFostering(models.Model):
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE, verbose_name=_('שם הכלב'))
    foster = models.ForeignKey(Foster, on_delete=models.CASCADE, verbose_name=_('שם האומנה'))
    fostering_date_start = models.DateField(default=datetime.date.today, verbose_name=_('תאריך תחילת האומנה'))
    fostering_date_end = models.DateField(blank=True, default=None, null=True, verbose_name=_('תאריך סיום האומנה'))
    fostering_comments = models.TextField(blank=True, default=None, null=True, verbose_name=_('הערות האומנה'))
    fostering_volunteer = models.TextField(blank=True, default=None, null=True, verbose_name=_('גורם מטפל בעמותה'))
    fostering_link_text = models.FileField(blank=True, default=None, null=True, verbose_name=_('קישור לטופס אומנה'))
    fostering_link_for_adoption_text = models.FileField(blank=True, default=None, null=True, verbose_name=_('קישור לטופס אומנה למטרת אימוץ'))

    def __str__(self):
        return "{}_{}".format(self.dog.__str__(), self.foster.__str__())


class CatAdoption(models.Model):
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, verbose_name=_('שם החתול'))
    adopter = models.ForeignKey(Adopter, on_delete=models.CASCADE, verbose_name=_('שם המאמצ/ת'))
    adoption_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך האימוץ'))
    method_of_payment = models.CharField(max_length=50, blank=True, default=None, null=True, verbose_name=_('שיטת התשלום'))
    receipt_number = models.IntegerField(blank=True, default=None, null=True, verbose_name=_('מספר חשבונית'))
    adoption_form_link = models.FileField(upload_to='mediaCats/', blank=True, default=None, null=True, verbose_name=_('קישור למסמך האימוץ'))
    adoption_comments = models.TextField(blank=True, default=None, null=True, verbose_name=_('הערות האימוץ'))
    last_followup_call = models.TextField(blank=True, default=None, null=True, verbose_name=_('שיחת מעקב אחרונה'))
    next_followup_call = models.DateField(default=None,blank=True, null=True, verbose_name=_('תאריך שיחת מעקב הבאה'))
    adoption_volunteer = models.TextField(blank=True, default=None, null=True, verbose_name=_('גורם מטפל באימוץ'))
    returned = models.BooleanField(default=False, verbose_name=_('החזרה'))
    return_date = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך החזרה'))
    return_reason = models.TextField(blank=True, default=None, null=True, verbose_name=_('סיבת החזרה'))
    waiver_document = models.FileField(upload_to='mediaCats/', blank=True, default=None, null=True, verbose_name=_('מסמך וויתור'))
    return_volunteer = models.TextField(blank=True, default=None, null=True, verbose_name=_('גורם מטפל בהחזרה'))

    def __str__(self):
        return "{}_{}".format(self.cat.__str__(), self.adopter.__str__())


class CatFostering(models.Model):
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, verbose_name=_('שם החתול'))
    foster = models.ForeignKey(Foster, on_delete=models.CASCADE, verbose_name=_('שם האומנה'))
    fostering_date_start = models.DateField(default=datetime.date.today, verbose_name=_('תאריך תחילת האומנה'))
    fostering_date_end = models.DateField(blank=True, default=None, null=True, verbose_name=_('תאריך סיום האומנה'))
    fostering_comments = models.TextField(blank=True, default=None, null=True, verbose_name=_('הערות האומנה'))
    fostering_volunteer = models.TextField(blank=True, default=None, null=True, verbose_name=_('גורם מטפל בעמותה'))
    fostering_link_text = models.FileField(blank=True, default=None, null=True, verbose_name=_('קישור לטופס אומנה'))
    fostering_link_for_adoption_text = models.FileField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לטופס אומנה למטרת אימוץ'))

    def __str__(self):
        return "{}_{}".format(str(self.cat.__str__()) + "_" + str(self.cat.id), self.foster.__str__())


class Volunteer(models.Model):
    name =  models.CharField(max_length=255, default=None, verbose_name=_('שם'))
    def __str__(self):
        return self.name


class Response(models.Model):
    response_owner = models.CharField(max_length=255, verbose_name=_('שם מטפלת'))
    status = models.CharField(max_length=255,  choices=STATUS_CHOICES, verbose_name=_('סטטוס'))
    comments = models.CharField(max_length=1000, verbose_name=_('הערות'))
    full_name = models.CharField(max_length=255, editable=False)
    age = models.IntegerField(editable=False)
    city = models.CharField(max_length=255, editable=False)
    phone_num = models.CharField(max_length=255, editable=False)
    mail = models.CharField(max_length=255,editable=False)
    maritalStatus =models.CharField(max_length=255,editable=False)
    numChildren = models.IntegerField(editable=False)
    otherPets =models.CharField(max_length=255, editable=False)
    experience = models.CharField(max_length=1000, editable=False)
    dog_name = models.CharField(max_length=500,editable=False)
    allergies = models.CharField(max_length=255,editable=False)
    own_apartment = models.CharField(max_length=255,editable=False)
    rent_agreed = models.CharField(max_length=255,editable=False)
    residenceType =models.CharField(max_length=255, editable=False)
    fence =models.CharField(max_length=255, editable=False)
    dogPlace = models.CharField(max_length=255,editable=False)
    dogSize =models.CharField(max_length=255, editable=False)
    response_comments =models.CharField(max_length=1000, editable=False)

    response_date = models.DateTimeField()
    QID = models.CharField(unique=True, max_length=50, editable=False)

    def __str__(self):
        return self.QID


class BlackList(models.Model):
    full_name = models.CharField(max_length=255, default=None, verbose_name=_('שם'))
    city = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('עיר מגורים'))
    mail = models.EmailField(max_length=254, blank=True, default=None, null=True, verbose_name=_('כתובת מייל'))
    phone_num = models.CharField(max_length=255, unique=True, verbose_name=_('מספר טלפון'))
    comments = models.CharField(max_length=400, default=None, verbose_name=_('הערות'))

    def __str__(self):
        return self.name

