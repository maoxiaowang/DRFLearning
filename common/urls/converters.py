import datetime


class DateStringConverter:
    """
    2022-10-20
    """
    regex = r'\d{4}-[0-1]\d{1}-[0-3]\d{1}'
    # regex = '[^/]+'

    def to_python(self, value):
        year, month, day = value.split('-')
        return datetime.date(year=int(year), month=int(month), day=int(day))

    def to_url(self, value):
        if isinstance(value, datetime.date):
            value = value.strftime('%Y-%m-%d')
        return value


class YearStringConverter:
    """
    1 - 3000
    """
    regex = r'[1-2]{1}[0-9]{3}'  # 1000 - 2999

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return value


class MonthStringConverter:
    """
    1 - 12
    """
    regex = r'0[1-9]|1[0-2]'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return value
