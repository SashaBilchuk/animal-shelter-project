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
    ('Association','עמותה'),('Foster','אומנה'),('Adoption','אימוץ')
)


class Dog(models.Model):
    id = models.AutoField(primary_key=True)
    chip_number = models.IntegerField(unique=True, verbose_name=_('מספר שבב'))
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    #age = models.IntegerField(default=0, verbose_name=_('גיל'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, null = False, verbose_name=_('מין'))
    image = models.ImageField(upload_to='mediaDogs/', default='media/generic_img.png',blank=True, verbose_name=_('הוסף תמונה'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=255, verbose_name=_('גודל'))
    color = models.CharField(max_length=255, verbose_name=_('צבע'))
    description = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('תיאור הכלב'))
    location = models.CharField(choices=PLACES, max_length=20, verbose_name=_('מיקום הכלב'))
    behaviour_description = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('תיאור התנהגותי'))
    acceptance_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך קבלה לעמותה'))
    number_of_days_in_the_association = models.IntegerField(default=1, verbose_name=_('מספר ימים בעמותה'))
    story = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('סיפור הכלב'))
    clinic = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('מרפאה וטרינרית'))
    notebook = models.BooleanField(default=False, verbose_name=_('יש פנקס חיסונים?'))
    rabbies_vaccine = models.DateField(blank=True, null = True, verbose_name=_('חיסון כלבת'))
    hexagonal_vaccine = models.DateField(blank=True, null = True, verbose_name=_('חיסון משושה'))
    nonagonal_vaccine = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתושע'))
    ocagonal_vaccine1 = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתומן 1'))
    ocagonal_vaccine2 = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתומן 2'))
    ocagonal_vaccine3 = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתומן 3'))
    worming = models.DateField(blank=True, null = True, verbose_name=_('תילוע'))
    simparica = models.DateField(blank=True, null = True, verbose_name=_('סימפריקה'))
    medical_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות רפואיות'))
    sterilization = models.DateField(blank=True, null = True, verbose_name=_('סירוס/ עיקור'))
    next_treatment = models.DateField(blank=True, null = True, verbose_name=_('תאריך הטיפול הבא'))
    next_treatment_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות לטיפול הבא'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת פטירה'))
    death_date = models.DateField(blank=True, null = True, verbose_name=_('תאריך המוות'))
    adopter_name = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('שם המאמצ/ת'))
    adoption_date = models.DateField(blank=True, null = True, verbose_name=_('תאריך אימוץ'))
    return_date = models.DateField(blank=True, null = True, verbose_name=_('תאריך החזרה'))
    reason_of_return = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת ההחזרה'))
    vaccine_book_url = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לפנקס חיסונים'))
    sterilization_approval_link = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לאישור סירוס/ עיקור'))
    rabbies_vaccine_aproval_link = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לאישור חיסון כלבת'))
    giveaway_forms = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מסמך החזרה'))
    waiver_forms = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מסמך העברה'))
    returner_id = models.IntegerField(default = 0, blank=True, null=True, verbose_name=_('תעודת זהות של מחזיר הכלב/ה'))
    #DisplayFields = ['age_years', 'age_months']

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

    def __str__(self):
        return self.name

    # def search(self, query=None):
    #     qs = self.get_queryset()
    #     if query is not None:
    #         or_lookup = (Q(title__icontains=query) |
    #                      Q(description__icontains=query)|
    #                      Q(slug__icontains=query)
    #                     )
    #         qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
    #     return qs

class Cat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    #age = models.IntegerField(default=0, verbose_name=_('גיל'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, verbose_name=_('מגדר'))
    image = models.ImageField(upload_to='mediaCats/', default='media/generic_img.png',blank=True, verbose_name=_('הוסף תמונה'))
    description = models.TextField(max_length=360, verbose_name=_('תיאור החתול/ה'))
    location = models.CharField(choices=PLACES, max_length=20, verbose_name=_('מיקום'))
    acceptance_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך קבלה לעמותה'))
    number_of_days_in_the_association = models.IntegerField(default=1, verbose_name=_('מספר ימים בעמותה'))
    story = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('סיפור החתול/ה'))
    notebook = models.BooleanField(default=False, verbose_name=_('פנקס חיסונים'))
    square_vaccine = models.BooleanField(default=False, verbose_name=_('חיסון מרובע'))
    ticks_fleas_treatment = models.DateField(default=None, verbose_name=_('טיפול קרציות ופרעושים'))
    sterilization = models.DateField(default=None, verbose_name=_('סירוס/ עיקור'))
    next_treatment = models.DateField(default=None, verbose_name=_('תאריך הטיפול הבא'))
    next_treatment_comments = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('הערות לטיפול הבא'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('סיבת פטירה'))
    death_date = models.DateField(blank=True, null = True, verbose_name=_('תאריך פטירה'))
    # adopter_name = models.TextField(max_length=255, blank=True, default=None,null = True)
    # adopter_ID = models.ForeignKey('Adopter', on_delete=models.PROTECT)
    adopter_id = models.IntegerField(default=None,blank=True, null=True, verbose_name=_('ת.ז של מאמץ'))
    vaccine_book_url = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('קישור לפנקס חיסונים'))
    sterilization_approval_link = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('קישור לאישור סירוס/ עיקור'))
    #DisplayFields = ['age_years', 'age_months']

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

    def __str__(self):
        return self.name

# class Adopter(models.Model):
#     adopter_ID = models.IntegerField(unique=True, default=None)
#     name = models.CharField(max_length=255, default=None)
#
#     def __str__(self):
#         return self.name

# class Foster(models.Model):
#     id = models.AutoField(primary_key=True)
#     foster_ID = models.IntegerField(unique=True, default=None, verbose_name=_('ת.ז'))
#     name = models.CharField(max_length=255, default=None, verbose_name=_('שם'))
#
#     def __str__(self):
#         return self.name


    # name = models.CharField(max_length=255)
    # birth_date = models.DateField(default=datetime.date.today)
    # age = models.IntegerField(default=0)
    # gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    # image = models.ImageField(upload_to='mediaCats/')
    # description = models.TextField(max_length=360)
    # acceptance_date = models.DateField(default=datetime.date.today)
    # number_of_days_in_the_association = models.IntegerField(default=1)
    # story = models.TextField(max_length=255, blank=True, default=None,null = True)
    # notebook = models.BooleanField(default=False)
    # square_vaccine = models.BooleanField(default=False)
    # ticks_fleas_treatment = models.DateField(default=None)
    # sterilization = models.DateField(default=None)
    # next_treatment = models.DateField(default=None)
    # next_treatment_comments = models.TextField(max_length=255, blank=True, default=None,null = True)
    # died = models.BooleanField(default=False)
    # death_reason = models.TextField(max_length=255, blank=True, default=None,null = True)
    # # death_date = models.DateField(default=None, blank=True, null = True)
    # death_date = models.DateField(blank=True, null = True)
    # location = models.CharField(choices=PLACES, max_length=6)
    # adopter_name = models.TextField(max_length=255, blank=True, default=None,null = True)
    # adopter_id = models.IntegerField(default=None,blank=True, null=True)
    # vaccine_book_url = models.TextField(max_length=255, blank=True, default=None,null = True)
    # sterilization_approval_link = models.TextField(max_length=255, blank=True, default=None,null = True)
    # def __str__(self):
    #     return self.name



