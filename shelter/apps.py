from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# class ShelterConfig(AppConfig):
#     name = 'shelters'
#
class DogsConfig(AppConfig):
    name = 'dogs'
    verbose_name = _('כלבים')


class CatsConfig(AppConfig):
    name = 'cats'
    verbose_name = _('חתולים')

# class FosterConfig(AppConfig):
#     name = 'fosters'