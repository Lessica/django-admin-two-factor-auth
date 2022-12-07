from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _


class TwoFactorAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    2fa code logins.
    """

    code = forms.CharField(
        label=_("2FA Code"),
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "off"}),
        validators=[
            RegexValidator(r'^\d{6}$', _('Enter a valid 2FA code.'), 'invalid'),
        ],
    )

    error_messages = {
        "invalid_login": _("You are not allowed to access this page. Please log in first."),
        "invalid_2fa_code": _("Please enter a correct 2FA code. Note that 2FA codes are time-sensitive."),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        code = self.cleaned_data.get("code")

        if code is not None:
            self.user_cache = self.request.user
            if not self.user_cache or not self.user_cache.is_authenticated:
                raise ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
            else:
                self.confirm_login_allowed(self.user_cache, code)
        else:
            raise self.get_invalid_2fa_code_error()

        return self.cleaned_data

    def confirm_login_allowed(self, user, code):
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )
        elif hasattr(user, 'two_factor') and user.two_factor.is_active:
            if not user.two_factor.verify(code):
                raise self.get_invalid_2fa_code_error()

    def get_user(self):
        return self.user_cache

    def get_invalid_2fa_code_error(self):
        return ValidationError(
            self.error_messages["invalid_2fa_code"],
            code="invalid_2fa_code",
            params={"code": self.fields["code"].label},
        )
