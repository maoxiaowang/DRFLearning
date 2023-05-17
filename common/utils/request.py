import functools
import typing
from io import BytesIO
from pathlib import Path

import requests
import urllib3
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.files.temp import NamedTemporaryFile
from django.core.validators import URLValidator
from django.utils.crypto import get_random_string
from requests.exceptions import JSONDecodeError

from common.exceptions import ProjectException
from common.logging import loggers
from common.utils.text import get_filename

__all__ = [
    'get_file',
    'get_image',
    'BaseRequest',
    'RequestFailed'
]

MAX_RETRY_TIMES = 3
urllib3.disable_warnings()


def respond_as_json(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            respond = func(self, *args, **kwargs)
        except Exception as e:
            loggers.request.error(str(e), exc_info=e)
            raise
        try:
            data = respond.json()
        except JSONDecodeError:
            return {'status_code': respond.status_code, 'reason': respond.reason}
        return data

    return wrapper


def set_headers(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        params = kwargs.pop('params', {})
        kwargs['params'] = self._get_params(**params)
        headers = kwargs.pop('headers', dict())
        kwargs['headers'] = self._get_headers(headers)
        return func(self, *args, **kwargs)

    return wrapper


def get_file(
        url,
        filename: str = None,  # 文件名，如果没有后缀将根据url自动添加后缀
        file_class=File,  # 默认File类
        session=None,  # requests.Session，携带context
        use_origin_filename=False,  # 是否使用原始文件名，默认为False，将以32位随机字符串命名
) -> typing.Union[File, None]:
    """
    通过requests下载文件，生成返回File对象
    """
    if not url:
        # None, ""
        return
    if not session:
        session = requests.session()
    path = Path(url)
    if filename and not filename.endswith(path.suffix):
        filename += path.suffix
    else:
        if use_origin_filename:
            filename = get_filename(url)
        else:
            filename = get_random_string(32) + path.suffix

    # 请求文件下载
    response = None
    for c in range(MAX_RETRY_TIMES):
        try:
            response = session.get(url)
        except Exception as e:
            loggers.request.error(e)
            continue
        else:
            break
    if not response:
        loggers.request.error('Failed to save image: %s' % url)
        return file_class(BytesIO())

    # 写入命名临时文件
    content = response.content
    img_temp = NamedTemporaryFile()
    img_temp.write(content)
    img_temp.flush()

    return file_class(img_temp, name=filename)


def get_image(url, filename: str = None, session=None, **kwargs):
    """
    通过requests下载图片，返回ImageFile对象
    """
    return get_file(
        url, filename=filename, file_class=ImageFile, session=session, **kwargs
    )


class BaseRequest(object):
    base_url = None
    token_name = 'token'
    token_value = None
    default_headers = {'Content-Type': 'application/json'}
    default_params = dict()

    def __new__(cls, *args, **kwargs):
        super_new = super().__new__
        if cls.base_url:
            URLValidator()(cls.base_url)
        return super_new(cls)

    def __init__(self, **kwargs):
        self.base_url = kwargs.pop('base_url', self.base_url)
        if not self.base_url:
            raise NotImplementedError("The attribute 'base_url' is required.")
        self.base_url = self.base_url.rstrip('/')
        token_name = kwargs.pop('token_name', self.token_name)
        token_value = kwargs.pop('token_value', self.token_value)
        self.token = None
        # 默认方式设置token
        self.token = {'name': token_name, 'value': token_value} if token_value else None

        self.session = requests.session()

    def _full(self, path):
        return self.base_url + '/' + path.lstrip('/')

    def _get_headers(self, headers=None):
        headers = headers or dict()
        assert isinstance(headers, dict)
        headers.update(self.default_headers)
        return headers

    def _get_params(self, **kwargs: dict):
        if self.token:
            kwargs.update({self.token['name']: self.token['value']})
        return kwargs

    @respond_as_json
    @set_headers
    def get(self, path, params=None, **kwargs):
        params = params or dict()
        params = self._get_params(**params)
        _headers = kwargs.pop('headers', dict())
        headers = self._get_headers(_headers)
        return self.session.get(
            self._full(path), params=params, verify=False, headers=headers, **kwargs
        )

    @respond_as_json
    def post(self, path, data=None, **kwargs):
        return self.session.post(self._full(path), data=data, verify=False, **kwargs)

    @respond_as_json
    def put(self, path, data=None, **kwargs):
        return self.session.put(self._full(path), data=data, verify=False, **kwargs)

    @respond_as_json
    def delete(self, path, **kwargs):
        return self.session.delete(self._full(path), **kwargs)

    def get_file(self, path, name=None):
        return get_file(path, filename=name, session=self.session)

    def get_image(self, path, name=None):
        return get_image(path, filename=name, session=self.session)


class RequestFailed(ProjectException):
    def __init__(self, code, msg=None, **kwargs):
        self.msg = msg or ''
        self.kwargs = kwargs
        self.code = code

    def __str__(self):
        return '[%s] %s' % (self.code, self.msg)
