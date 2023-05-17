import threading
import uuid

from django.utils.deprecation import MiddlewareMixin

local = threading.local()

__all__ = [
    'CommonMiddleware',
]


class CommonMiddleware(MiddlewareMixin):

    def process_request(self, request):
        local.request_id = request.META.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)
        setattr(request, 'request_id', local.request_id)

    def process_response(self, request, response):
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = local.request_id if hasattr(local, 'request_id') else None
        try:
            del local.request_id
        except AttributeError:
            pass
        return response

    # def process_exception(self, request, exception):
    #     if hasattr(request, 'request_id'):
    #         ...
