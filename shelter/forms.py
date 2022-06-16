from django import forms
import datetime
from .models import Dog, Cat, Adopter, Foster, DogAdoption, CatAdoption, CatFostering, DogFostering, BlackList, \
                    Response, STATUS_CHOICES


class AddDog(forms.ModelForm):
    class Meta:
        model = Dog
        fields = "__all__"
        exclude = ['foster_relation_dog', 'adopter_relation_dog']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}),
                   'acceptance_date': forms.DateInput(attrs={'type': 'date'}),
                   'exit_date': forms.DateInput(attrs={'type': 'date'}),
                   'physical_description': forms.Textarea(attrs={'rows': 3}),
                   'behaviour_description': forms.Textarea(attrs={'rows': 3}),
                   'story': forms.Textarea(attrs={'rows': 3}),
                   'clinic': forms.Textarea(attrs={'rows': 3}),
                   'worming_1': forms.DateInput(attrs={'type': 'date'}),
                   'worming_2': forms.DateInput(attrs={'type': 'date'}),
                   'hexagonal_vaccine': forms.DateInput(attrs={'type': 'date'}),
                   'next_treatment_hexagonal': forms.DateInput(attrs={'type': 'date'}),
                   'rabies_vaccine': forms.DateInput(attrs={'type': 'date'}),
                   'next_treatment_rabies': forms.DateInput(attrs={'type': 'date'}),
                   'ticks_fleas_treatment': forms.DateInput(attrs={'type': 'date'}),
                   'next_ticks_fleas_treatment': forms.DateInput(attrs={'type': 'date'}),
                   'sterilization': forms.DateInput(attrs={'type': 'date'}),
                   'medical_comments': forms.Textarea(attrs={'rows': 3}),
                   'death_date': forms.DateInput(attrs={'type': 'date'}),
                   'death_reason': forms.Textarea(attrs={'rows': 3})}

    def clean_acceptance_date(self):
        acceptance_date = self.cleaned_data['acceptance_date']
        if acceptance_date > datetime.date.today():
            raise forms.ValidationError("תאריך כניסה לעמותה לא יכול להיות בעתיד - נא להזין תאריך תקין")
        return acceptance_date

    # def clean_exit_date(self):
    #     exit_date = self.data['exit_date']
    #     acceptance_date = self.data['acceptance_date']
    #     if exit_date and acceptance_date:
    #         if exit_date < acceptance_date:
    #             raise forms.ValidationError("תאריך יציאה מעמותה לא יכול להיות לפני תאריך הכניסה - נא להזין תאריך תקין")
    #     return datetime.date.today()



class AddCat(forms.ModelForm):
    class Meta:
        model = Cat
        fields = "__all__"
        exclude = ['foster_relation_cat', 'adopter_relation_cat']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}),
                   'acceptance_date': forms.DateInput(attrs={'type': 'date'}),
                   'exit_date': forms.DateInput(attrs={'type': 'date'}),
                   'physical_description': forms.Textarea(attrs={'rows': 3}),
                   'behaviour_description': forms.Textarea(attrs={'rows': 3}),
                   'story': forms.Textarea(attrs={'rows': 3}),
                   'clinic': forms.Textarea(attrs={'rows': 3}),
                   'ticks_fleas_treatment': forms.DateInput(attrs={'type': 'date'}),
                   'next_ticks_fleas_treatment': forms.DateInput(attrs={'type': 'date'}),
                   'sterilization': forms.DateInput(attrs={'type': 'date'}),
                   'medical_comments': forms.Textarea(attrs={'rows': 3}),
                   'death_date': forms.DateInput(attrs={'type': 'date'}),
                   'death_reason': forms.Textarea(attrs={'rows': 3})}

    def clean_acceptance_date(self):
        acceptance_date = self.cleaned_data['acceptance_date']
        if acceptance_date > datetime.date.today():
            raise forms.ValidationError("תאריך כניסה לעמותה לא יכול להיות בעתיד - נא להזין תאריך תקין")
        return acceptance_date

    def clean_exit_date(self):
        exit_date = self.cleaned_data['exit_date']
        acceptance_date = Cat.acceptance_date
        if exit_date and acceptance_date:
            if exit_date < acceptance_date:
                raise forms.ValidationError("תאריך יציאה מעמותה לא יכול להיות לפני תאריך הכניסה - נא להזין תאריך תקין")
        return exit_date


class AddAdopter(forms.ModelForm):
    class Meta:
        model = Adopter
        fields = "__all__"
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}),
                   'ID_link': forms.Textarea(attrs={'rows': 3}),
                   'adopter_comments': forms.Textarea(attrs={'rows': 3})
                   }


class AddFoster(forms.ModelForm):
    class Meta:
        model = Foster
        fields = "__all__"
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}),
                   'ID_link': forms.Textarea(attrs={'rows': 3}),
                   'foster_comments': forms.Textarea(attrs={'rows': 3})
                   }


class DogAdoptionsForm(forms.ModelForm):
    class Meta:
        model = DogAdoption
        fields = "__all__"
        widgets = {'adoption_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments': forms.Textarea(attrs={'rows': 3}),
                   'last_followup_call': forms.Textarea(attrs={'rows': 3}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_volunteer': forms.Textarea(attrs={'rows': 3}),
                   'return_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['dog'].queryset = Dog.objects.filter(location="Association")


    def clean_adoption_date(self):
        adoption_date = self.cleaned_data['adoption_date']
        if adoption_date > datetime.date.today():
            raise forms.ValidationError("תאריך אימוץ לא יכול להיות בעתיד - נא להזין תאריך תקין")
        return adoption_date

    # def clean_return_date(self):
    #     return_date = self.data['return_date']
    #     adoption_date = self.data['adoption_date']
    #     if return_date and adoption_date:
    #         if return_date < adoption_date:
    #             raise forms.ValidationError("תאריך החזרה לא יכול להיות לפני תאריך האימוץ - נא להזין תאריך תקין")
    #     return datetime.date.today()


    # def clean_dog(self):
    #     dog = self.cleaned_data.get('dog')
    #     for instance in DogAdoption.objects.all():
    #         if instance.dog == dog:
    #             raise forms.ValidationError(dog.name + ' כבר אומצ/ה')
    #     return dog


class DogAdoptionsEdit(forms.ModelForm):
    class Meta:
        model = DogAdoption
        fields = "__all__"
        widgets = {'adoption_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments': forms.Textarea(attrs={'rows': 3}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_volunteer': forms.Textarea(attrs={'rows': 3}),
                   'return_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dog'].disabled = True
        self.fields['adopter'].disabled = True
        self.fields['adoption_date'].disabled = True


class DogFosteringForm(forms.ModelForm):
    class Meta:
        model = DogFostering
        fields = "__all__"
        widgets = {'fostering_date_start': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_date_end': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_comments': forms.Textarea(attrs={'rows': 3}),
                   'fostering_volunteer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['dog'].queryset = Dog.objects.filter(location="Association")

    # def clean_dog(self):
    #     dog = self.cleaned_data.get('dog')
    #     for instance in DogFostering.objects.all():
    #         if instance.dog == dog:
    #             raise forms.ValidationError(dog.name + ' כבר באומנה')
    #     return dog

    def clean_fostering_date_start(self):
        fostering_date_start = self.cleaned_data['fostering_date_start']
        if fostering_date_start > datetime.date.today():
            raise forms.ValidationError("תאריך תחילת האומנה לא יכול להיות בעתיד - נא להזין תאריך תקין")
        return  fostering_date_start

    # def clean_fostering_date_end(self):
    #     fostering_date_start = self.data['fostering_date_start']
    #     fostering_date_end = self.data['fostering_date_end']
    #     if fostering_date_start and fostering_date_end:
    #         if fostering_date_end < fostering_date_start:
    #             raise forms.ValidationError("תאריך סיום האומנה לא יכול להיות לפני תאריך תחילת האומנה - נא להזין תאריך תקין")
    #     return datetime.date.today()


class DogFosteringEdit(forms.ModelForm):
    class Meta:
        model = DogFostering
        fields = "__all__"
        widgets = {'fostering_date_start': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_date_end': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_comments': forms.Textarea(attrs={'rows': 3}),
                   'fostering_volunteer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dog'].disabled = True
        self.fields['foster'].disabled = True
        self.fields['fostering_date_start'].disabled = True


class CatAdoptionsForm(forms.ModelForm):
    class Meta:
        model = CatAdoption
        fields = "__all__"
        widgets = {'adoption_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments': forms.Textarea(attrs={'rows': 3}),
                   'last_followup_call': forms.Textarea(attrs={'rows': 3}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_volunteer': forms.Textarea(attrs={'rows': 3}),
                   'return_date': forms.DateInput(attrs={'type': 'date'}),
                   'return_reason': forms.Textarea(attrs={'rows': 3}),
                   'return_volunteer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['cat'].queryset = Cat.objects.filter(location="Association")

    # def clean_cat(self):
    #     cat = self.cleaned_data.get('cat')
    #     for instance in CatAdoption.objects.all():
    #         if instance.cat == cat:
    #             raise forms.ValidationError(cat.name + ' כבר אומצ/ה')
    #     return cat

    def clean_adoption_date(self):
        adoption_date = self.cleaned_data['adoption_date']
        if adoption_date > datetime.date.today():
            raise forms.ValidationError("תאריך אימוץ לא יכול להיות בעתיד - נא להזין תאריך תקין")
        return adoption_date

    # def clean_return_date(self):
    #     return_date = self.data['return_date']
    #     adoption_date = self.data['adoption_date']
    #     if return_date and adoption_date:
    #         if return_date < adoption_date:
    #             raise forms.ValidationError("תאריך החזרה לא יכול להיות לפני תאריך האימוץ - נא להזין תאריך תקין")
    #     return datetime.date.today()


class CatAdoptionsEdit(forms.ModelForm):
    class Meta:
        model = CatAdoption
        fields = "__all__"
        widgets = {'adoption_date': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_comments': forms.Textarea(attrs={'rows': 3}),
                   'next_followup_call': forms.DateInput(attrs={'type': 'date'}),
                   'adoption_volunteer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].disabled = True
        self.fields['adopter'].disabled = True
        self.fields['adoption_date'].disabled = True


class CatFosteringForm(forms.ModelForm):
    class Meta:
        model = CatFostering
        fields = "__all__"
        widgets = {'fostering_date_start': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_date_end': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_comments': forms.Textarea(attrs={'rows': 3}),
                   'fostering_volunteer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['cat'].queryset = Cat.objects.filter(location="Association")

    # def clean_cat(self):
    #     cat = self.cleaned_data.get('cat')
    #     for instance in CatFostering.objects.all():
    #         if instance.cat == cat:
    #             raise forms.ValidationError(cat.name + ' כבר באומנה')
    #     return cat

    def clean_fostering_date_start(self):
        fostering_date_start = self.cleaned_data['fostering_date_start']
        if fostering_date_start > datetime.date.today():
            raise forms.ValidationError("תאריך תחילת האומנה לא יכול להיות בעתיד - נא להזין תאריך תקין")
        return fostering_date_start

    # def clean_fostering_date_end(self):
    #     fostering_date_start = self.data['fostering_date_start']
    #     fostering_date_end = self.data['fostering_date_end']
    #     if fostering_date_start and fostering_date_end:
    #         if fostering_date_end < fostering_date_start:
    #             raise forms.ValidationError(
    #                 "תאריך סיום האומנה לא יכול להיות לפני תאריך תחילת האומנה - נא להזין תאריך תקין")
    #     return datetime.date.today()


class CatFosteringEdit(forms.ModelForm):
    class Meta:
        model = CatFostering
        fields = "__all__"
        widgets = {'fostering_date_start': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_date_end': forms.DateInput(attrs={'type': 'date'}),
                   'fostering_comments': forms.Textarea(attrs={'rows': 3}),
                   'fostering_volunteer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].disabled = True
        self.fields['foster'].disabled = True
        self.fields['fostering_date_start'].disabled = True


class BlackListForm(forms.ModelForm):
    class Meta:
        model = BlackList
        fields = "__all__"
        widgets = {'full_name': forms.Textarea(attrs={'rows': 1}),
                   'city': forms.Textarea(attrs={'rows': 1}),
                   'mail ': forms.EmailInput(),
                   'phone_num ': forms.Textarea(attrs={'rows': 1}),
                   'comments ': forms.Textarea(attrs={'rows': 3})}

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
        widgets = {"comments": forms.Textarea(attrs={'rows': 3})}

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
        widgets = {'city': forms.Textarea(attrs={'rows': 1}),
                   'mail ': forms.EmailInput(),
                   "comments": forms.Textarea(attrs={'rows': 3})}