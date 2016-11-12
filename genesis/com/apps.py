from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class ComConfig(AppConfig):
    name = 'com'
    verbose_name = _('Accounting')
