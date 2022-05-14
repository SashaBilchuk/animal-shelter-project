from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DogsConfig(AppConfig):
    name = 'dogs'
    verbose_name = _('כלבים')


class CatsConfig(AppConfig):
    name = 'cats'
    verbose_name = _('חתולים')


class AdoptersConfig(AppConfig):
    name = 'adopters'
    verbose_name = _('מאמצים')

