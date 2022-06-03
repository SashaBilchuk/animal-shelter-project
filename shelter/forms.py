from django import forms
import datetime
from .models import Dog, Cat, DogAdoption, CatAdoption, CatFostering, DogFostering,BlackList, Response, STATUS_CHOICES
from django.utils.translation import gettext_lazy as _


# STATUS_CHOICES = (
#     ('adopted', 'אימץ מהעמותה'),
#     ('adoption_approved', 'מאושר לאימוץ'),
#     ('first_call', 'בוצעה שיחה ראשונית'),
#     ('video_call_wait', 'ממתינים לוידאו'),
#     ('pending', 'טרם טופל'),
#     ('not_approved', 'לא מתאים לאימוץ'),
#     ('black_list', 'רשימה שחורה')
# )


class AddDog(forms.ModelForm):
    class Meta:
        model = Dog
        fields = "__all__"
        exclude = ['foster_relation_dog', 'adopter_relation_dog']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}),
                   'physical_description': forms.Textarea(attrs={'rows': 3}),
                   'acceptance_date': forms.DateInput(attrs={'type': 'date'}),
                   'next_treatment_rabies': forms.DateInput(attrs={'type': 'date'}),
                   'death_date': forms.DateInput(attrs={'type': 'date'})}

    def clean_acceptance_date(self):
        date = self.cleaned_data['acceptance_date']
        if date > datetime.date.today():
            raise forms.ValidationError("תאריך לא יכול להיות בעתיד")
        return date


class DogAdoptionsForm(forms.ModelForm):
    class Meta:
        model = DogAdoption
        fields = ['dog', 'adopter', 'adoption_date', 'method_of_payment', 'receipt_number', 'adoption_form_link',
                  'adoption_comments', 'next_followup_call', 'adoption_volunteer']
        widgets = {'adoption_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments': forms.Textarea(attrs={'rows': 3}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_volunteer': forms.Textarea(attrs={'rows': 3})}

    def clean_dog(self):
        dog = self.cleaned_data.get('dog')
        for instance in DogAdoption.objects.all():
            if instance.dog == dog:
                raise forms.ValidationError(dog.name + 'כבר אומצ/ה')
        return dog


class DogFosteringForm(forms.ModelForm):
    class Meta:
        model = DogFostering
        fields = "__all__"
        widgets = {'fostering_date_start': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_date_end': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_comments': forms.Textarea(attrs={'rows': 3}),
                   'fostering_volunteer': forms.Textarea(attrs={'rows': 3}),
                   'fostering_link_text': forms.Textarea(attrs={'rows': 3}),
                   'fostering_link_for_adoption_text': forms.Textarea(attrs={'rows': 3})
                   }

    def clean_dog(self):
        dog = self.cleaned_data.get('dog')
        for instance in DogFostering.objects.all():
            if instance.dog == dog:
                raise forms.ValidationError(dog.name + ' כבר באומנה')
        return dog


class CatAdoptionsForm(forms.ModelForm):
    class Meta:
        model = CatAdoption
        fields = ['cat', 'adopter', 'adoption_date', 'method_of_payment', 'receipt_number', 'adoption_form_link',
                  'adoption_comments', 'next_followup_call', 'adoption_volunteer']
        widgets = {'adoption_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments': forms.Textarea(attrs={'rows': 3}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_volunteer': forms.Textarea(attrs={'rows': 3})}

    def clean_cat(self):
        cat = self.cleaned_data.get('cat')
        for instance in CatAdoption.objects.all():
            if instance.cat == cat:
                raise forms.ValidationError(cat.name + ' כבר אומצ/ה')
        return cat


class CatFosteringForm(forms.ModelForm):
    class Meta:
        model = CatFostering
        fields = "__all__"
        widgets = {'fostering_date_start': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_date_end': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_comments': forms.Textarea(attrs={'rows': 3}),
                   'fostering_volunteer': forms.Textarea(attrs={'rows': 3}),
                   'fostering_link_text': forms.Textarea(attrs={'rows': 3}),
                   'fostering_link_for_adoption_text': forms.Textarea(attrs={'rows': 3})
                   }

    def clean_cat(self):
        cat = self.cleaned_data.get('cat')
        for instance in CatFostering.objects.all():
            if instance.cat == cat:
                raise forms.ValidationError(cat.name + ' כבר באומנה')
        return cat


class BlackListForm(forms.ModelForm):
    class Meta:
        model = BlackList
        fields = "__all__"
        widgets = {'full_name': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
                   'city': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
                   'mail ': forms.EmailInput(),
                   'phone_num ': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
                   'comments ': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})}

    def clean_response(self):
        existing_phones = self.cleaned_data.get('phone_num')
        for instance in BlackList.objects.all():
            if instance.phone_num == existing_phones:
                raise forms.ValidationError(instance.name + ' קיים ברשימה')
        return existing_phones


class EditResponseStatus(forms.ModelForm):

    class Meta:
        model = Response
        fields = ("response_owner", "status",  "comments")
        # {"status": forms.Select(choices=STATUS_CHOICES, attrs={'class': 'form-control'}),
        widgets = {"status": forms.ChoiceField(choices=STATUS_CHOICES),
                    "response_owner": forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
                   "comments": forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
                   }

    # def clean_response(self):
    #     existing_phones = self.cleaned_data.get('phone_num')
    #     for instance in BlackList.objects.all():
    #         if instance.phone_num == existing_phones:
    #             raise forms.ValidationError(instance.name + ' קיים ברשימה')
    #     return existing_phones

class EditBlackListForm(forms.ModelForm):
    class Meta:
        model = BlackList
        fields = "__all__"
        # {"status": forms.Select(choices=STATUS_CHOICES, attrs={'class': 'form-control'}),
        widgets = {'full_name': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
                   'city': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
                   'mail ': forms.EmailInput(),
                   'phone_num ': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
                   'comments ': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})}