from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
import uuid
from django.utils.translation import gettext_lazy as _

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
    ('ACTIVE ADOPTION', 'אימץ',), ('RETURNED', 'החזיר')
     )


class Adopter(models.Model):
    adopter_ID = models.IntegerField(unique=True, default=None)
    name = models.CharField(max_length=255, default=None)
    ID_link = models.TextField(max_length=255, blank=True, default=None, null = True, verbose_name=_('קישור לת"ז'))
    adopter_city = models.TextField(max_length=255, blank=True, default=None, null = True, verbose_name=_('עיר מגורים'))
    adopter_street = models.TextField(max_length=255, blank=True, default=None, null = True, verbose_name=_('רחוב'))
    phone_number = models.CharField(max_length=12,default=None, blank=True, null=True, verbose_name=_('מספר טלפון'))
    email_address = models.EmailField(max_length=254, blank=True, default=None, null = True, verbose_name=_('כתובת מייל'))
    activity_status = models.CharField(choices=STATUS_ADOPTER,default='אימץ', max_length=20, verbose_name=_('סטטוס פעילות'))
    black_listed = models.BooleanField(default=False, verbose_name=_('רשימה שחורה'))


    def __str__(self):
        return self.name


class Dog(models.Model):
    id = models.AutoField(primary_key=True)
    chip_number = models.IntegerField(blank=True, default=None, null=True, verbose_name=_('מספר שבב'))
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, verbose_name=_('מין'))
    physical_description = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('תיאור חיצוני'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=255, blank=True, default=None, null=True, verbose_name=_('גודל'))
    color = models.CharField(max_length=255, blank=True, default=None, null=True, verbose_name=_('צבע'))
    behaviour_description = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('תיאור התנהגותי'))
    story = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיפור רקע'))
    image = models.ImageField(upload_to='mediaDogs/', default='media/generic_img.png', blank=True, null=True, verbose_name=_('תמונה'))
    location = models.CharField(max_length=255, choices=PLACES, blank=True, default=None, null=True, verbose_name=_('מיקום הכלב'))
    acceptance_date = models.DateField(default=datetime.date.today,blank=True, null=True, verbose_name=_('תאריך קבלה לעמותה'))
    #exit_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך יציאה מעמותה'))
    clinic = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מרפאה וטרינרית'))
    vaccine_book = models.BooleanField(default=False, verbose_name=_('פנקס חיסונים'))
    vaccine_book_url = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('קישור לפנקס חיסונים'))
    hexagonal_vaccine = models.DateField(blank=True, null=True, verbose_name=_('חיסון משושה'))
    next_treatment_hexagonal = models.DateField(blank=True, null=True, verbose_name=_('משושה - תאריך הטיפול הבא'))
    nonagonal_vaccine = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתושע'))
    ocagonal_vaccine1 = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתומן 1'))
    ocagonal_vaccine2 = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתומן 2'))
    ocagonal_vaccine3 = models.DateField(blank=True, null=True, verbose_name=_('חיסון מתומן 3'))
    worming = models.DateField(blank=True, null=True, verbose_name=_('תילוע'))
    next_treatment_worming = models.DateField(blank=True, null=True, verbose_name=_('תילוע - תאריך הטיפול הבא'))
    simparica = models.DateField(blank=True, null=True, verbose_name=_('סימפריקה'))
    next_treatment_simparica = models.DateField(blank=True, null=True, verbose_name=_('סימפריקה - תאריך הטיפול הבא'))
    sterilization = models.DateField(blank=True, null=True, verbose_name=_('סירוס/עיקור'))
    sterilization_approval = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('אישור סירוס/עיקור'))
    rabies_vaccine = models.DateField(blank=True, null=True, verbose_name=_('חיסון כלבת'))
    next_treatment_rabies = models.DateField(blank=True, null=True, verbose_name=_('כלבת - תאריך הטיפול הבא'))
    rabies_vaccine_approval = models.FileField(upload_to='mediaDogs/', blank=True, default=None, null=True, verbose_name=_('אישור חיסון כלבת'))
    next_treatment_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות לטיפולים הבאים'))
    medical_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות רפואיות'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_date = models.DateField(blank=True, null=True, verbose_name=_('תאריך הפטירה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת הפטירה'))
    adopter_relation_dog = models.ManyToManyField(Adopter, through='DogAdoption', related_name="adoptions_dog")



    @property
    def age_years(self):
        if self.birth_date is not None:
            return datetime.date.today().year - self.birth_date.year
        else:
            return 0

    @property
    def age_months(self):
        if self.birth_date is not None:
            return datetime.date.today().month - self.birth_date.month
        else:
            return 0

    @property
    def days_in_the_association(self):
        if self.acceptance_date is not None and self.location == 'Association':
            return datetime.date.today().day - self.acceptance_date.day
        else:
            return 0

    @property
    def get_adopters(self):
        adopters = self.adopter_relation_dog.all()
        print(type(adopters))
        return adopters

    def __str__(self):
        return self.name


class Cat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, verbose_name=_('מין'))
    image = models.ImageField(upload_to='mediaCats/', blank=True, null=True, default='media/generic_img.png', verbose_name=_('תמונה'))
    description = models.TextField(max_length=360, blank=True, default=None, null=True, verbose_name=_('תיאור החתול/ה'))
    location = models.CharField(choices=PLACES, blank=True, default=None, null=True, max_length=20, verbose_name=_('מיקום'))
    acceptance_date = models.DateField(default=datetime.date.today,blank=True, null=True, verbose_name=_('תאריך קבלה לעמותה'))
    story = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיפור החתול/ה'))
    sterilization = models.DateField(default=None, blank=True, null=True, verbose_name=_('סירוס/עיקור'))
    sterilization_approval = models.ImageField(upload_to='mediaCats/', blank=True, default=None, null=True, verbose_name=_('אישור סירוס/עיקור'))
    notebook = models.BooleanField(default=False, verbose_name=_('פנקס חיסונים'))
    vaccine_book_url = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לפנקס חיסונים'))
    square_vaccine = models.BooleanField(default=False, verbose_name=_('חיסון מרובע'))
    ticks_fleas_treatment = models.DateField(default=None, blank=True, null=True, verbose_name=_('טיפול קרציות ופרעושים'))
    next_treatment = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך הטיפול הבא'))
    next_treatment_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות לטיפול הבא'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת הפטירה'))
    death_date = models.DateField(default=None, blank=True, null=True, verbose_name=_('תאריך הפטירה'))
    adopter_relation_cat = models.ManyToManyField(Adopter, through='CatAdoption', related_name="adoptions_cat")


    @property
    def age_years(self):
        if self.birth_date is not None:
            return datetime.date.today().year - self.birth_date.year
        else:
            return 0

    def age_months(self):
        if self.birth_date is not None:
            return datetime.date.today().month-self.birth_date.month
        else:
            return 0

    @property
    def days_in_the_association(self):
        if self.acceptance_date is not None:
            return datetime.date.today().day - self.acceptance_date.day
        else:
            return 0

    @property
    def get_adopters(self):
        adopters = self.adopter_relation_cat.all()
        print(type(adopters))
        return adopters

    def __str__(self):
        return self.name


class DogAdoption(models.Model):
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE, verbose_name=_('כלב'))
    adopter = models.ForeignKey(Adopter, on_delete=models.CASCADE, verbose_name=_('מאמץ'))
    adoption_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך אימוץ'))

    def __str__(self):
        return "{}_{}".format(self.adopter.__str__(), self.dog.__str__())


class CatAdoption(models.Model):
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, verbose_name=_('חתול'))
    adopter = models.ForeignKey(Adopter, on_delete=models.CASCADE, verbose_name=_('מאמץ'))
    adoption_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך אימוץ'))

    def __str__(self):
        return "{}_{}".format(self.adopter.__str__(), self.cat.__str__())
    
    
# class Foster(models.Model):
#     id = models.AutoField(primary_key=True)
#     foster_ID = models.IntegerField(unique=True, default=None, verbose_name=_('ת.ז'))
#     name = models.CharField(max_length=255, default=None, verbose_name=_('שם'))
#
#     def __str__(self):
#         return self.name





