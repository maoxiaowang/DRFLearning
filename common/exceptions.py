import typing

from common.utils.text import str2int
from common.views.response import Response
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError, ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import status as http_status
from rest_framework.views import set_rollback
from rest_framework_simplejwt.exceptions import InvalidToken

__all__ = [
    'exception_handler',
    'ProjectException'
]


def construct_messages(msg: typing.Union[str, dict, list]) -> list:
    if not msg:
        return msg
    msg_list = list()
    if isinstance(msg, dict):
        for field, values in msg.items():
            if isinstance(values, list):
                try:
                    value = ';'.join(values)
                except TypeError:
                    # not string items
                    msg_list.extend(construct_messages(values))
                else:
                    item = f'[{field}] {value}' if settings.DEBUG else value
                    msg_list.append(item)
            else:
                item = f'[{field}] {values}' if settings.DEBUG else values
                msg_list.append(item)
    elif isinstance(msg, list):
        for item in msg:
            try:
                msg_list.extend(construct_messages(item))
            except TypeError:
                raise
    else:
        msg_list.append(str(msg))

    return msg_list


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default, we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    # 项目异常
    if isinstance(exc, ProjectException):
        exc = exceptions.APIException(detail=exc.desc, code=exc.code)

    # Django异常
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(detail=exc.message, code=exc.code)
    elif isinstance(exc, ObjectDoesNotExist):
        exc = exceptions.NotFound(detail=str(exc), code=http_status.HTTP_404_NOT_FOUND)

    # jwt token异常
    if isinstance(exc, InvalidToken):
        exc = exceptions.APIException(
            detail=_('Token is invalid or expired'),
            code=InvalidToken.status_code
        )
        exc.status_code = InvalidToken.status_code

    # DRF异常处理
    if isinstance(exc, exceptions.APIException):
        data = None
        msg = None
        headers = {}
        auth_header = getattr(exc, 'auth_header', None)
        if auth_header:
            headers['WWW-Authenticate'] = auth_header
        wait = getattr(exc, 'wait', None)
        if wait:
            headers['Retry-After'] = '%d' % wait
        if isinstance(exc, exceptions.ValidationError):
            msg = exc.detail
        else:
            if isinstance(exc.detail, (list, dict)):
                data = exc.detail
            else:
                msg = exc.detail

        msg = construct_messages(msg)
        status = exc.status_code
        set_rollback()
        return Response(data=data, msg=msg, status=status, headers=headers, context=context)


class ProjectException(Exception):
    level = 'error'
    desc = _('Undefined exception')
    code = 400

    def __init__(self, desc=None, **kwargs):
        self.desc = desc or self.desc
        code = str2int(kwargs.get('code'))
        if code:
            self.code = code
        level = kwargs.get('level')
        if level in ('error', 'warning', 'info', 'debug'):
            self.level = level
        self.kwargs = kwargs

    def __str__(self):
        return str(self.desc)
