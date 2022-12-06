from django.conf import settings

# Two factor name
ADMIN_2FA_NAME = getattr(settings, 'ADMIN_TWO_FACTOR_NAME', None)

# two factor session expire time (in seconds)
SESSION_2FA_AGE = getattr(settings, 'SESSION_COOKIE_AGE', 7200)
