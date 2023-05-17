"""
String helper
"""
import decimal
import hashlib
import json
import os
import re
import sys
import typing
import uuid
from datetime import datetime, date, time
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.functional import Promise

__all__ = [
    'is_int', 'is_float', 'is_list', 'is_dict', 'is_tuple', 'is_bool',
    'str_len', 'str2int', 'str2float', 'str2digit', 'str2bool',
    'str2base', 'str2iter', 'percent_str2float', 'camel2underline', 'underline2camel',
    'comma_separated_str2list', 'query_str2dict',
    'obj2iter', 'md5_encode', 'get_filename', 'get_filename_extension',
    'CJsonEncoder', 'is_json_str',
    'crypto_mobile'
]

# Notice: Following regex patterns are not accurate, may cause unexpected errors

REGEX_INT = r'^-?\d+$'
REGEX_FLOAT = r'^-?\d+\.\d+$'
REGEX_LIST = r'^\[.*?\]$'
REGEX_DICT = r'^({[\"\'].*?[\"\'].*?:.*})'
REGEX_TUPLE = r'^(\(.*?\)|\(\))$'
REGEX_BOOL = r'^(true|false)'


def is_int(obj):
    if isinstance(obj, str):
        return bool(re.match(REGEX_INT, obj))
    elif isinstance(obj, int):
        return True
    return False


def is_float(obj: typing.Union[float, str]):
    if isinstance(obj, str):
        return bool(re.match(REGEX_FLOAT, obj))
    elif isinstance(obj, float):
        return True
    return False


def is_list(obj: typing.Union[list, str], json_required=True):
    if isinstance(obj, str) and re.match(REGEX_LIST, obj):
        if json_required:
            try:
                json.loads(obj)
            except json.JSONDecodeError:
                return False
        return True
    elif isinstance(obj, list):
        return True
    return False


def is_dict(obj, json_required=True):
    if isinstance(obj, str) and re.match(REGEX_DICT, obj):
        if json_required:
            try:
                json.loads(obj)
            except json.JSONDecodeError:
                return False
        return True
    elif isinstance(obj, dict):
        return True
    return False


def is_tuple(obj):
    if isinstance(obj, tuple):
        return True
    elif isinstance(obj, str) and re.match(REGEX_TUPLE, obj):
        return True
    return False


def is_bool(string, strict=True):
    flags = 0
    if not strict:
        flags = re.IGNORECASE
    return bool(re.match(REGEX_BOOL, string, flags=flags))


def str_len(string):
    """
    Chinese characters or other non-ascii chars
    will be traded as two ascii chars
    """
    length = None
    encoding = sys.getdefaultencoding()
    if encoding == 'utf-8':
        # Linux liked system
        length = len(string.encode('gbk'))
    else:
        # when system encoding is not utf-8
        pass
    return length


def str2int(string, default: int = None, raise_exc=False):
    """Raise exceptions if default is None"""
    if isinstance(string, int):
        return string
    elif isinstance(string, str):
        if is_int(string):
            return int(string)
        else:
            if default is not None:
                return default
            if raise_exc:
                raise ValueError
    else:
        if default is not None:
            return default
        if raise_exc:
            raise TypeError


def str2float(string, default=None, raise_exc=False) -> float:
    """Raise exceptions if default is None"""
    if isinstance(string, float):
        return string
    elif isinstance(string, str):
        if re.match(r'^-?\d+\.?\d*$', string):
            return float(string)
        else:
            if default is not None:
                return default
            if raise_exc:
                raise ValueError
    else:
        if default is not None:
            return default
        if raise_exc:
            raise TypeError


def str2digit(string, default=None, raise_exc=False):
    """
    String to int or float
    """
    if isinstance(string, (int, float)):
        return string
    elif isinstance(string, str):
        if is_int(string):
            return str2int(string, default=default, raise_exc=raise_exc)
        elif re.match(REGEX_FLOAT, string):
            return str2float(string, default=default, raise_exc=raise_exc)
        else:
            if default is not None:
                return default
            if raise_exc:
                raise ValueError
    if default is not None:
        return default
    if raise_exc:
        raise TypeError


def str2bool(string, default: bool = None, silent=False):
    """
    str to bool
    """
    if isinstance(string, bool):
        return string
    elif isinstance(string, str):
        if string in ('true', 'True'):
            return True
        elif string in ('false', 'False'):
            return False
        else:
            if default is not None:
                return default
            if not silent:
                raise ValueError
    else:
        if default is not None:
            return default
        if not silent:
            raise TypeError


def str2base(string):
    """
    Turn string to Base type (int, float, bool or str),
    not including list, dict ...
    """
    if not isinstance(string, str):
        return string
    if is_int(string):
        return int(string)
    elif is_float(string):
        return float(string)
    elif string in ('true', 'True'):
        return True
    elif string in ('false', 'False'):
        return False
    else:
        return string


def str2iter(string):
    """
    Turn string to list, tuple, set or str
    """
    if not isinstance(string, str):
        return string
    if is_list(string) or is_dict(string) or is_tuple(string):
        return eval(string)
    return string


def obj2iter(obj):
    """
    Simply translate an common object to an iterable object.
    Non-iterable object will be turned to a list.
    """
    return obj if isinstance(obj, (list, tuple, dict)) else [obj]


def percent_str2float(string, silent=False, default=0):
    """
    '85.4%' --> 85.4
    """
    if '%' not in string:
        raise ValueError
    try:
        string = re.findall(r'(\d+(\.\d+)?)%', string)[0][0]
    except IndexError:
        if silent:
            string = default
        else:
            raise
    return str2float(string)


def camel2underline(string, smart: bool = False):
    """
    驼峰转下划线
    smart为True时会特殊处理连续大写的情况
    """
    assert isinstance(string, str)
    if not string:
        return string
    word = str()
    word_list = list()
    for i, s in enumerate(string):
        if i == 0:
            word += s.lower()
            continue
        if smart and s.isupper():
            if string[i - 1].upper():
                # 前面也是大写
                if i < len(string) - 1:
                    # 后面还有字母
                    if string[i + 1].isupper():
                        s = s.lower()
                else:
                    s = s.lower()
            else:
                s = s.lower()
        if s.isupper():
            word_list.append(word)
            word = s.lower()
        else:
            word += s
    word_list.append(word)
    return '_'.join(word_list)


def underline2camel(string, smart: bool = None):
    assert isinstance(string, str)
    assert smart is None, 'The smart argument is not supported.'
    if not string:
        return string
    word_list = string.split('_')
    return ''.join([item.capitalize() for item in word_list])


def comma_separated_str2list(string, default=None):
    if not string:
        return default
    return string.split(',')


def query_str2dict(string, default=None):
    """
    queryset查询字符串转为字典
    """
    if not string:
        return default

    # 逗号隔开的条件，转成列表
    # 如 name=hello,id__in=1,2,3,datetime__range=2022-01-10T09:00:00Z,2022-02-01T09:00:00Z
    # 转为 ['name=hello', 'id__in=1,2,3', 'datetime__range=2022-01-10T09:00:00Z,2022-02-01T09:00:00Z']
    # 注意，条件中可能有逗号
    result_list = list()
    items = [s for s in string.split(',')]
    for i, item in enumerate(items):
        if not item:
            continue
        split_items = item.split('=')
        if len(split_items) > 2:
            raise ValueError
        elif len(split_items) == 1:
            if len(result_list) > 0:
                # id__in=1,2,3
                result_list[-1] += f',{split_items[0]}'
            else:
                # 1,2,3
                raise ValueError
        else:
            result_list.append(item)

    # 组合为条件字典
    result_dict = dict()
    for item in result_list:
        try:
            k, v = item.split('=')
        except ValueError:
            raise
        result_dict.update({k: v})
    return result_dict


def md5_encode(string):
    """
    Hash a string with MD5
    """
    assert isinstance(string, str)
    m2 = hashlib.md5()
    m2.update(string.encode())
    return m2.hexdigest()


def get_filename(url):
    try:
        # if it is an url
        URLValidator(url)
    except ValidationError:
        # not a url
        return url

    path = urlparse(url).path
    filename = os.path.basename(path)
    return filename


def get_filename_extension(filename):
    """
    examples:
    abc.xyz -> .xyz
    abc.xxx.yyy.zzz?v=1 -> .zzz
    https://www.xxx.com/abc.xyz -> .abc.xyz

    可使用Path(filename).suffix代替
    """
    filename = get_filename(filename)
    return Path(filename).suffix
    # res = re.findall(r'^.*\.(.*)$', filename)
    # extension = res[0] if res else ''
    # return extension if extension and intact else extension


SENSITIVE_FIELDS = ['password']


class CJsonEncoder(json.JSONEncoder):
    objects_to_string = (decimal.Decimal, uuid.UUID, Promise)

    def default(self, obj):
        if isinstance(obj, datetime):
            return timezone.localtime(obj).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            obj = datetime(obj.year, obj.month, obj.day, 0, 0, 0, tzinfo=timezone.get_current_timezone())
            return timezone.localdate(obj).strftime('%Y-%m-%d')
        elif isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, self.objects_to_string):
            return str(obj)
        elif obj.__class__.__name__ == 'GenericRelatedObjectManager':
            return
        elif isinstance(obj, FieldFile):
            if obj:
                return obj.url
        elif isinstance(obj, Model):
            return model_to_dict(obj, exclude=SENSITIVE_FIELDS)
        else:
            return json.JSONEncoder.default(self, obj)


def is_json_str(raw_str):
    if isinstance(raw_str, str):
        try:
            json.loads(raw_str)
        except ValueError:
            return False
        return True
    else:
        return False


def crypto_mobile(mobile_phone):
    if not mobile_phone:
        return mobile_phone
    return re.sub(r'^(\+?\d{3})\d{4}(\d+)$', r'\1****\2', mobile_phone)
