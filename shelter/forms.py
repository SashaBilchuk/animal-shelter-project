from django import forms
from .models import Dog, Cat, DogAdoption, CatAdoption #, ShelterHistory
from django.utils.translation import gettext_lazy as _


class DogDeathForm(forms.ModelForm):
    class Meta:
        model = Dog
        fields = ['death_date']
        # fromDate = Dog.acceptance_date
        # toDate = Dog.acceptance_date
        widgets = {'death_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})}

class DogAdoptionsForm(forms.ModelForm):
    class Meta:
        model = DogAdoption
        fields = "__all__"
        widgets = {'adoption_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                   'next_followup_call': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
                   'return_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
                   'adoption_comments ': forms.Textarea(attrs={'class': 'form-control','rows': 3})}

    def clean_dog(self):
        dog = self.cleaned_data.get('dog')
        for instance in DogAdoption.objects.all():
            if instance.dog == dog:
                raise forms.ValidationError(dog.name + ' כבר אומצ/ה')
        return dog

class CatAdoptionsForm(forms.ModelForm):
    class Meta:
        model = CatAdoption
        fields = "__all__"

        widgets = {'adoption_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'dir': 'rtl'}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'return_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments ': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})}

    def clean_cat(self):
        cat = self.cleaned_data.get('cat')
        for instance in CatAdoption.objects.all():
            if instance.cat == cat:
                raise forms.ValidationError(cat.name + ' כבר אומצ/ה')
        return cat

