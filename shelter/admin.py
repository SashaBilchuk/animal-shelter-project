from django.contrib import admin
from .models import Dog, Cat, Adopter, DogAdoption, CatAdoption

# from .models import Foster

# Register your models here.
admin.site.register(Dog)
admin.site.register(Cat)
admin.site.register(Adopter)
admin.site.register(DogAdoption)
admin.site.register(CatAdoption)


# admin.site.register(Foster)


