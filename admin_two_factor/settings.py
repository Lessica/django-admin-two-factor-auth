from django.conf import settings

# Two factor name
ADMIN_2FA_NAME = getattr(settings, 'ADMIN_2FA_NAME', None)

# two factor session expire time (in seconds)
SESSION_2FA_AGE = getattr(settings, 'SESSION_2FA_AGE', 7200)
