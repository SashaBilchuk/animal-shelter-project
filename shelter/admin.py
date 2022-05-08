from django.contrib import admin
from .models import Dog, Cat, Adopter, DogAdoption, CatAdoption

# from .models import Foster

# Register your models here.

class DogAdmin(admin.ModelAdmin):
    exclude = ('animal_type',)
admin.site.register(Dog, DogAdmin)
# admin.site.register(Dog)

class CatAdmin(admin.ModelAdmin):
    exclude = ('animal_type',)
admin.site.register(Cat, CatAdmin)
# admin.site.register(Dog)
# admin.site.register(Cat)
admin.site.register(Adopter)
admin.site.register(DogAdoption)
admin.site.register(CatAdoption)


# admin.site.register(Foster)


