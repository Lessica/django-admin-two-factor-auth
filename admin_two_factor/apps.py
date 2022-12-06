from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TwoFactorAuthenticationConfig(AppConfig):
    name = 'admin_two_factor'
    verbose_name = _('two factor')
