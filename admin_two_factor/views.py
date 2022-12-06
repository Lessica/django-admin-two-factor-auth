from urllib.parse import parse_qsl

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_protect

from admin_two_factor.utils import set_2fa_expiration


class TwoFactorAuthentication(View):

    @csrf_protect
    def post(self, request):
        params = dict(parse_qsl(request.body.decode()))
        username = params.get('username', None)
        password = params.get('password', None)
        if not username or not password:
            return JsonResponse(
                {'validated': False, 'message': _('Username and password are both required.')})
        user = authenticate(request=request, username=username, password=password)
        if user and user.is_staff:
            if hasattr(user, 'two_factor') and user.two_factor.is_active:
                return JsonResponse({'validated': True, '2fa-required': True, '2fa-passed': False,
                                     'message': _('Logged in successfully, but 2FA is required.')})
            return JsonResponse({'validated': True, '2fa-required': False, '2fa-passed': False,
                                 'message': _('Logged in successfully.')})
        return JsonResponse({'validated': False, 'message': _('Maybe something is wrong.')})

    @csrf_protect
    def put(self, request):
        params = dict(parse_qsl(request.body.decode()))
        tfa_code = params.get('2fa-code', None)
        username = params.get('username', None)
        password = params.get('password', None)
        if not username or not password:
            return JsonResponse({'validated': False, 'message': _('Username and password are both required.')})
        if not tfa_code:
            return JsonResponse(
                {'validated': False, 'message': _('Please provide a valid 2FA code, which is required.')})
        user = authenticate(request=request, username=username, password=password)
        if user and user.is_staff:
            if hasattr(user, 'two_factor') and user.two_factor.is_active:
                if user.two_factor.verify(tfa_code):
                    set_2fa_expiration(request)
                    return JsonResponse({'validated': True, '2fa-required': True, '2fa-passed': True,
                                         'message': _('Logged in successfully.')})
                else:
                    return JsonResponse(
                        {'validated': True, '2fa-required': True, '2fa-passed': False,
                         'message': _('Please provide a valid 2FA code, which is required.')})
            return JsonResponse({'validated': True, '2fa-required': False, '2fa-passed': False,
                                 'message': _('Logged in successfully.')})
        return JsonResponse({'validated': False, 'message': _('Maybe something is wrong.')})
