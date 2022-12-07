from django.urls import path

from admin_two_factor.views import TwoFactorAuthentication, logout

urlpatterns = [
    path('login/', TwoFactorAuthentication.as_view(), name='login'),
    path('logout/', logout, name='logout'),
]
