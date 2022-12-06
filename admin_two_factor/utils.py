import datetime
import time

from admin_two_factor import settings


def stamp_to_datetime(ts):
    """
    Convert seconds to datetime
    :param ts: This field should be in seconds
    :type ts: int field
    :return: date instance
    """
    date_time = datetime.datetime.fromtimestamp(ts)
    return date_time


def datetime_to_stamp(dt):
    """
    Convert datetime to seconds
    :param dt: This field should be in datetime
    :return: int
    """
    result = int(time.mktime(dt.timetuple()))
    return result


def set_2fa_expiration(request, interval=settings.SESSION_2FA_AGE):
    now_at = datetime.datetime.now()
    ex_time = datetime_to_stamp(now_at) + interval
    two_factor_key = 'two_factor_%s' % request.user.id
    two_factor_session = request.session[two_factor_key] if two_factor_key in request.session and isinstance(
        request.session[two_factor_key], dict) else {}
    two_factor_session.update({'expired_at': ex_time})
    request.session[two_factor_key] = two_factor_session


def is_2fa_expired(request, now=None):
    if not hasattr(request, 'user') or request.user is None:
        return True
    two_factor_key = 'two_factor_%s' % request.user.id
    two_factor_session = request.session[two_factor_key] if two_factor_key in request.session else None
    if two_factor_session is None:
        return True
    ex_time = two_factor_session['expired_at'] if 'expired_at' in two_factor_session else None
    if ex_time is None:
        return True
    now_at = datetime.datetime.now() if now is None else now
    return ex_time <= datetime_to_stamp(now_at)
