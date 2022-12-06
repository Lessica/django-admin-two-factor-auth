from django.urls import path

from admin_two_factor.views import TwoFactorAuthentication

urlpatterns = [
    path('2fa/', TwoFactorAuthentication.as_view(), name='2fa'),
]
