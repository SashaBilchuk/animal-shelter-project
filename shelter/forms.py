from django import forms
from .models import Dog, Cat, DogAdoption, CatAdoption #, ShelterHistory
from django.utils.translation import gettext_lazy as _

# class ShelterCreateForm(forms.ModelForm):
#     class Meta:
#         model = Shelter
#         fields = ['id', 'chip_number', 'name']
#
#     def clean_category(self):
#         category = self.cleaned_data.get('name') #was category- unknown??
#         if not category:
#             raise forms.ValidationError('This field is required')
#         return category
#
#     def clean_item_name(self):
#         item_name = self.cleaned_data.get('item_name')
#         if not item_name:
#             raise forms.ValidationError('This field is required')
#         for instance in Shelter.objects.all():
#             if instance.item_name == item_name:
#                 raise forms.ValidationError(str(item_name) + ' is already created')
#         return item_name
#
#
# class ShelterHistorySearchForm(forms.ModelForm):
#     export_to_CSV = forms.BooleanField(required=False)
#     start_date = forms.DateTimeField(required=False)
#     end_date = forms.DateTimeField(required=False)
#     class Meta:
#         model = Dog
#         fields = ['id', 'name', 'days_in_the_association', 'start_date', 'end_date']


class DogAdoptionsForm(forms.ModelForm):
    class Meta:
        model = DogAdoption
        fields = "__all__"
        widgets = {'adoption_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                   'next_followup_call': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
                   'return_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
                   'adoption_comments ': forms.Textarea(attrs={'class': 'form-control','rows': 3})}
        #help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).'), }


class CatAdoptionsForm(forms.ModelForm):
    class Meta:
        model = CatAdoption
        fields = "__all__"

        widgets = {'adoption_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'dir': 'rtl'}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'return_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments ': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})}
