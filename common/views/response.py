from typing import Union

from django.conf import settings
from django.core.files import File
from django.core.files.images import ImageFile
from rest_framework import status as http_status
from rest_framework.response import Response as _Response


class Response(_Response):

    @staticmethod
    def format_data(status=None, msg: list = None, data=None, context: dict = None):
        res = dict()
        if context and settings.DEBUG:
            # 出现异常，且debug开启时
            request = context['request']
            user = request.user
            wsgi_request = getattr(request, '_request')
            debug_data = request.data
            files: dict = getattr(request, '_files', {})
            file_fields = [field for field, value in files.items()] if files else list()
            for field in file_fields:
                value = debug_data[field]
                if isinstance(value, (File, ImageFile)):
                    debug_data[field] = value.name
                else:
                    debug_data[field] = 'Unknown file'

            debug_info = {
                'host': getattr(wsgi_request, '_current_scheme_host'),
                'path': wsgi_request.path,
                'method': wsgi_request.method,
                'data': debug_data,
                'user': {
                    'id': user.id if user.is_authenticated else None,
                    'username': user.username if user.is_authenticated else str(user)
                }
            }
            res['debug'] = debug_info
        res.update({
            'code': status or http_status.HTTP_200_OK,
            'msg': msg or [],
            'data': data if data is not None else {}
        })
        return res

    def __init__(self, data: Union[dict, list] = None, status=None, msg: list = None, *args, **kwargs):
        context = kwargs.pop('context', None)
        data = self.format_data(status=status, msg=msg, data=data, context=context)
        super().__init__(data=data, status=status, *args, **kwargs)
