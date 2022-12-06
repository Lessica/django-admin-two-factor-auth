from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from admin_two_factor.utils import is_2fa_expired, set_2fa_expiration


class TwoFactorMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and user.is_staff and \
                hasattr(user, 'two_factor') and user.two_factor.is_active:
            if is_2fa_expired(request):
                logout(request)
                messages.error(request, _('Your 2FA session has expired. Please log in again.'))
                return redirect('admin:login')
            else:
                set_2fa_expiration(request)  # reset expiration time
        response = self.get_response(request)
        return response
