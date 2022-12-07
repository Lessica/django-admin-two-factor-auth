from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login, RedirectURLMixin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as gettext
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from admin_two_factor.forms import TwoFactorAuthenticationForm
from admin_two_factor.utils import set_2fa_expiration, is_2fa_expired


@never_cache
@csrf_protect
def logout(request):
    return logout_then_login(request, "admin:login")


class TwoFactorAuthentication(RedirectURLMixin, View):
    next_page = "admin:index"

    def __init__(self, **kwargs):
        self.site_title = gettext("Django site admin")
        self.site_header = admin.site.site_header
        super().__init__(**kwargs)

    def each_context(self, request):
        script_name = request.META["SCRIPT_NAME"]
        return {
            "site_title": self.site_title,
            "site_header": self.site_header,
            "site_url": script_name,
            "has_permission": True,
            "available_apps": list(),
            "is_popup": False,
            "is_nav_sidebar_enabled": False,
        }

    def redirect_to_success_url(self, request):
        redirect_to = self.get_success_url()
        if redirect_to == self.request.path:
            redirect_to = self.get_default_redirect_url()
        return HttpResponseRedirect(redirect_to)

    @method_decorator(never_cache)
    @method_decorator(login_required(redirect_field_name="r", login_url="admin:login"))
    def get(self, request):
        if not is_2fa_expired(request):
            return self.redirect_to_success_url(request)
        return TemplateResponse(request, "admin_two_factor/login.html", context={
            **self.each_context(request),
            "title": gettext("Two-factor authentication"),
            "subtitle": None,
            "app_path": request.get_full_path(),
            "username": request.user.get_username(),
            "form": TwoFactorAuthenticationForm(),
            "next": request.GET.get(self.redirect_field_name, reverse(self.next_page)),
        })

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    @method_decorator(login_required(redirect_field_name="r", login_url="admin:login"))
    def post(self, request):
        if not is_2fa_expired(request):
            return self.redirect_to_success_url(request)
        form = TwoFactorAuthenticationForm(request, data=request.POST)
        if form.is_valid():  # 2fa code is valid
            set_2fa_expiration(request)
            return self.redirect_to_success_url(request)
        # 2fa code is invalid, error message is already set in form
        return TemplateResponse(request, "admin_two_factor/login.html", context={
            **self.each_context(request),
            "title": gettext("Two-factor authentication"),
            "subtitle": None,
            "app_path": request.get_full_path(),
            "username": request.user.get_username(),
            "form": form,
            "next": request.POST.get(self.redirect_field_name,
                                     request.GET.get(self.redirect_field_name, reverse(self.next_page))),
        })
