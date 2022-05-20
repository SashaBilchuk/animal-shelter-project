from django.contrib import admin
from .models import Dog, Cat, Adopter, DogAdoption, CatAdoption, Foster,\
    DogFostering,CatFostering, Volunteer

# from .models import Foster

# Register your models here.

class DogAdmin(admin.ModelAdmin):
    exclude = ('animal_type',)
admin.site.register(Dog, DogAdmin)
# admin.site.register(Dog)

class CatAdmin(admin.ModelAdmin):
    exclude = ('animal_type',)
admin.site.register(Cat, CatAdmin)

admin.site.register(Adopter)
admin.site.register(DogAdoption)
admin.site.register(CatAdoption)
admin.site.register(Foster)
admin.site.register(DogFostering)
admin.site.register(CatFostering)
admin.site.register(Volunteer)





