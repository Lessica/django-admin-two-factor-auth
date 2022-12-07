from django.contrib.auth.views import redirect_to_login
from django.urls import resolve

from admin_two_factor.utils import is_2fa_expired, set_2fa_expiration


class TwoFactorMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        next_path = None
        this_path = request.path_info
        now_login_page = False
        user = request.user
        url_resolver = resolve(request.path_info)
        if (url_resolver.app_name == 'admin') and \
                not (url_resolver.url_name == 'login' or url_resolver.url_name == 'logout'):
            if user and user.is_authenticated and user.is_staff:
                if hasattr(user, 'two_factor') and user.two_factor.is_active:
                    if is_2fa_expired(request):
                        return redirect_to_login(this_path, '2fa:login')
                    else:
                        set_2fa_expiration(request)
        elif url_resolver.app_name == 'admin' and url_resolver.url_name == 'login':
            if request.method == 'POST':
                if not user or not user.is_authenticated:
                    next_path = request.POST.get('next', None)
                    now_login_page = True
        response = self.get_response(request)
        if now_login_page:
            user = request.user
            if user and user.is_authenticated and user.is_staff:
                if hasattr(user, 'two_factor') and user.two_factor.is_active:
                    return redirect_to_login(next_path if next_path else this_path, '2fa:login')
        return response
