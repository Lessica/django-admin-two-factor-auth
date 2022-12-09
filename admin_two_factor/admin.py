from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.translation import gettext as _

from admin_two_factor.models import TwoFactorAuthentication
from admin_two_factor.utils import set_2fa_expiration


class TwoFactorAuthenticationForm(forms.ModelForm):
    class Meta:
        model = TwoFactorAuthentication
        fields = '__all__'
        widgets = {
            'code': forms.TextInput(attrs={'autocomplete': 'off'}),
        }


@admin.register(TwoFactorAuthentication)
class TwoFactorAuthenticationAdmin(admin.ModelAdmin):
    form = TwoFactorAuthenticationForm
    list_display = ['user', 'is_active', 'created_time']
    autocomplete_fields = ['user']
    list_select_related = ['user']

    def qrcode(self, obj):
        secret_key, qr_link = obj.get_qrcode
        if qr_link:
            return format_html(
                "<img src=\"data:image/png;base64,{qrcode}\" width=\"200\" alt=\"two factor authentication\">",
                qrcode=qr_link)
    qrcode.short_description = _('Two Factor QR Code')

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {'qrcode': format_html(
            "{desc} <a href=\"https://support.google.com/accounts/answer/1066447?hl=en\" target=\"_blank\">{link}</a>",
                desc=_("Scan the following barcode with your phone’s OTP app (e.g. Google Authenticator)."),
                link=_("Install Google Authenticator?")
            )}
        kwargs.update({'help_texts': help_texts})
        return super(TwoFactorAuthenticationAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            if request.user.is_superuser:
                return [
                    (None, {
                        'fields': ['user', ],
                    }),
                ]
            return []
        else:
            if obj.secret:
                if request.user.is_superuser:
                    return [
                        (None, {
                            'fields': ['user', 'is_active', 'code'],
                        }),
                        (_("History"), {
                            "fields": ["created_time", "updated_time"],
                        }),
                    ]
                else:
                    return [
                        (None, {
                            'fields': ['is_active', 'code'],
                        }),
                        (_("History"), {
                            "fields": ["created_time", "updated_time"],
                        }),
                    ]
            else:
                if request.user.is_superuser:
                    return [
                        (None, {
                            'fields': ['user', 'is_active', 'code', 'qrcode'],
                        }),
                        (_("History"), {
                            "fields": ["created_time", "updated_time"],
                        }),
                    ]
                else:
                    return [
                        (None, {
                            'fields': ['is_active', 'code', 'qrcode'],
                        }),
                        (_("History"), {
                            "fields": ["created_time", "updated_time"],
                        }),
                    ]

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ['is_active', 'created_time']
        return []

    def get_search_fields(self, request):
        if request.user.is_superuser:
            return ['user__username']
        return []

    def get_queryset(self, request):
        qs = super(TwoFactorAuthenticationAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['created_time', 'updated_time']
        if obj is not None or not request.user.is_superuser:
            readonly_fields.append('user')
        readonly_fields.append('qrcode')
        return readonly_fields

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return obj is None or obj.user == request.user or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return obj is None or obj.user == request.user or request.user.is_superuser

    def has_module_permission(self, request):
        return True

    def response_add(self, request, obj, post_url_continue=None):
        self.message_user(request, _('user added successfully'), level=messages.SUCCESS)
        return redirect('admin:admin_two_factor_twofactorauthentication_change', obj.id)

    def response_change(self, request, obj):
        set_2fa_expiration(request)
        return super(TwoFactorAuthenticationAdmin, self).response_change(request, obj)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if not self.get_object(request, object_id):
            extra_context['show_save_and_add_another'] = False
        return super(TwoFactorAuthenticationAdmin, self).changeform_view(request, object_id, form_url, extra_context)
