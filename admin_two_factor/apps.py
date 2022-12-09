from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


def user_logged_in_callback(sender, **kwargs):
    user = kwargs.get('user', None)
    if user is not None:
        from admin_two_factor.models import TwoFactorAuthentication
        TwoFactorAuthentication.objects.get_or_create(user=user)


class TwoFactorAuthenticationConfig(AppConfig):
    name = 'admin_two_factor'
    verbose_name = _('two factor')

    def ready(self):
        from django.contrib.auth.signals import user_logged_in
        user_logged_in.connect(user_logged_in_callback)
