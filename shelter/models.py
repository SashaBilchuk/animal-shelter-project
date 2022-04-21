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


class Dog(models.Model):
    id = models.AutoField(primary_key=True)
    chip_number = models.IntegerField(blank=True, default=None, null=True, verbose_name=_('מספר שבב'))
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, verbose_name=_('מין'))
    image = models.ImageField(upload_to='mediaDogs/', default='media/generic_img.png', blank=True, verbose_name=_('הוסף תמונה'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=255, verbose_name=_('גודל'))
    color = models.CharField(max_length=255, verbose_name=_('צבע'))
    description = models.TextField(max_length=255, blank=True, default=None, null = True, verbose_name=_('תיאור הכלב'))
    behaviour_description = models.TextField(max_length=255, blank=True, default=None, null=True,verbose_name=_('תיאור התנהגותי'))
    location = models.CharField(choices=PLACES, max_length=20, verbose_name=_('מיקום הכלב'))
    acceptance_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך קבלה לעמותה'))
    exit_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך יציאה מעמותה'))
    story = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיפור הכלב'))
    clinic = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מרפאה וטרינרית'))
    sterilization = models.DateField(blank=True, null=True, verbose_name=_('סירוס/עיקור'))
    sterilization_approval = models.ImageField(upload_to='mediaDogs/', blank=True, default=None, verbose_name=_('אישור סירוס/עיקור'))
    notebook = models.BooleanField(default=False, verbose_name=_('יש פנקס חיסונים?'))
    vaccine_book_url = models.TextField(max_length=255, blank=True, default=None, null=True,verbose_name=_('קישור לפנקס חיסונים'))
    rabies_vaccine = models.DateField(blank=True, null = True, verbose_name=_('חיסון כלבת'))
    next_treatment_rabies = models.DateField(blank=True, null=True, verbose_name=_('כלבת - תאריך הטיפול הבא'))
    rabies_vaccine_approval = models.ImageField(upload_to='mediaDogs/', null=False, default=None, verbose_name=_('אישור חיסון כלבת'))
    hexagonal_vaccine = models.DateField(blank=True, null = True, verbose_name=_('חיסון משושה'))
    next_treatment_hexagonal = models.DateField(blank=True, null = True, verbose_name=_('משושה - תאריך הטיפול הבא'))
    nonagonal_vaccine = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתושע'))
    ocagonal_vaccine1 = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתומן 1'))
    ocagonal_vaccine2 = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתומן 2'))
    ocagonal_vaccine3 = models.DateField(blank=True, null = True, verbose_name=_('חיסון מתומן 3'))
    worming = models.DateField(blank=True, null = True, verbose_name=_('תילוע'))
    next_treatment_worming = models.DateField(blank=True, null=True, verbose_name=_('תילוע - תאריך הטיפול הבא'))
    simparica = models.DateField(blank=True, null = True, verbose_name=_('סימפריקה'))
    next_treatment_simparica = models.DateField(blank=True, null=True, verbose_name=_('סימפריקה - תאריך הטיפול הבא'))
    medical_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות רפואיות'))
    next_treatment_comments = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('הערות לטיפול הבא'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_date = models.DateField(blank=True, null=True, verbose_name=_('תאריך הפטירה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת פטירה'))
    adopter_id = models.IntegerField(default=None, blank=True, null=True, verbose_name=_('ת.ז. של המאמצ/ת'))
    adopter_name = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('שם המאמצ/ת'))
    adoption_date = models.DateField(blank=True, null = True, verbose_name=_('תאריך אימוץ'))
    waiver_forms = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מסמך העברה'))
    returner_id = models.IntegerField(default=0, blank=True, null=True, verbose_name=_('ת.ז. של מחזיר הכלב/ה'))
    return_date = models.DateField(blank=True, null = True, verbose_name=_('תאריך החזרה'))
    reason_of_return = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיבת ההחזרה'))
    giveaway_forms = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('מסמך החזרה'))


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

    def __str__(self):
        return self.name


class Cat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name=_('שם'))
    birth_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך לידה'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, verbose_name=_('מין'))
    image = models.ImageField(upload_to='mediaCats/', default='media/generic_img.png', blank=True, verbose_name=_('הוסף תמונה'))
    description = models.TextField(max_length=360, verbose_name=_('תיאור החתול/ה'))
    location = models.CharField(choices=PLACES, max_length=20, verbose_name=_('מיקום'))
    acceptance_date = models.DateField(default=datetime.date.today, verbose_name=_('תאריך קבלה לעמותה'))
    story = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('סיפור החתול/ה'))
    sterilization = models.DateField(default=None, verbose_name=_('סירוס/עיקור'))
    sterilization_approval = models.ImageField(upload_to='mediaCats/', blank=True, default=None, verbose_name=_('אישור סירוס/עיקור'))
    notebook = models.BooleanField(default=False, verbose_name=_('פנקס חיסונים'))
    vaccine_book_url = models.TextField(max_length=255, blank=True, default=None, null=True, verbose_name=_('קישור לפנקס חיסונים'))
    square_vaccine = models.BooleanField(default=False, verbose_name=_('חיסון מרובע'))
    ticks_fleas_treatment = models.DateField(default=None, verbose_name=_('טיפול קרציות ופרעושים'))
    next_treatment = models.DateField(default=None, verbose_name=_('תאריך הטיפול הבא'))
    next_treatment_comments = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('הערות לטיפול הבא'))
    died = models.BooleanField(default=False, verbose_name=_('נפטר/ה'))
    death_reason = models.TextField(max_length=255, blank=True, default=None,null = True, verbose_name=_('סיבת פטירה'))
    death_date = models.DateField(blank=True, null = True, verbose_name=_('תאריך פטירה'))
    # adopter_name = models.TextField(max_length=255, blank=True, default=None,null = True)
    # adopter_ID = models.ForeignKey('Adopter', on_delete=models.PROTECT)
    adopter_id = models.IntegerField(default=None,blank=True, null=True, verbose_name=_('ת.ז של המאמצ/ת'))



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





