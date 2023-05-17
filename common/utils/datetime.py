import datetime
import re
import typing

import pytz
from django.utils import timezone

STANDARD_FORMAT = '%Y-%m-%d %H:%M:%S'
ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
FILENAME_FORMAT = '%Y%m%d_%H%M%S'
DATE_HYPHEN_FORMAT = '%Y-%m-%d'
DATE_SLASH_FORMAT = '%d/%m/%Y'


def to_aware_datetime(dt: typing.Union[str, datetime.datetime, datetime.date], tz=None):
    """
    Make a naive datetime using a given timezone(tz)

    Notice: tz if the timezone of dt, make sure they are matched
    """
    if dt is None:
        return
    if tz is None:
        tz = timezone.get_current_timezone()
    else:
        if isinstance(tz, str):
            tz = pytz.timezone(tz)
    if isinstance(dt, (datetime.datetime, datetime.date)):
        if timezone.is_aware(dt):
            return dt
        else:
            # Asia/Shanghai, same to settings
            return timezone.make_aware(dt, timezone=tz)
    elif isinstance(dt, str):
        dt = str_to_datetime(dt)
        aware = timezone.make_aware(dt, timezone=tz)
        return aware
    raise ValueError


def str_to_datetime(date_string, fmt=STANDARD_FORMAT) -> datetime.datetime:
    """
    Support style:
    2018-12-07T06:24:24.000000
    2018-12-07T06:24:24Z
    2018-12-07 06:24:24
    2018-12-7
    ...
    """
    ds = re.findall(r'^(\d{4}-\d{2}-\d{2})[T\s]?(\d{2}:\d{2}:\d{2})?.*$', date_string)
    if not ds:
        raise ValueError('Invalid datetime string: %s' % date_string)
    year_month_day, hour_minute_second = ds[0]
    if not hour_minute_second:
        year, month, day = year_month_day.split('-')
        return datetime.datetime(year=int(year), month=int(month), day=int(day))
    else:
        date_string = '%s %s' % (year_month_day, hour_minute_second)
        return datetime.datetime.strptime(date_string, fmt)


def datetime_to_str(dt: datetime.datetime = None, fmt=STANDARD_FORMAT) -> str:
    dt = dt or datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    assert isinstance(dt, datetime.datetime)
    dt_string = datetime.datetime.strftime(dt, fmt)
    return dt_string


def date_to_str(dt: datetime.date = None, fmt='%Y-%m-%d') -> str:
    dt = dt or timezone.now().date()
    assert isinstance(dt, datetime.date)
    return dt.strftime(fmt)


def get_date_from_datetime(dt: str) -> str:
    ds = re.findall(r'^(\d{1,4}-\d{2}-\d{2})[T\s]?.*', dt)
    if not ds:
        raise ValueError('Invalid datetime string: %s' % dt)
    return ds[0]
