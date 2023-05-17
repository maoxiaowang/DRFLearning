import functools

from rest_framework import exceptions
from rest_framework.permissions import BasePermission, DjangoModelPermissions

from common.utils.text import camel2underline


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class BaseModelPermissions(DjangoModelPermissions):

    get = []
    head = []
    option = []
    post = ['%(app_label)s.add_%(model_underline_name)s']
    put = ['%(app_label)s.change_%(model_underline_name)s']
    delete = ['%(app_label)s.delete_%(model_underline_name)s']
    patch = ['%(app_label)s.change_%(model_underline_name)s']
    strict_get = ['%(app_label)s.view_%(model_underline_name)s']

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            # 将queryset赋值给view，否则多查询一次
            if view.queryset is None:
                view.queryset = view.get_queryset()
            assert view.queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
        return view.queryset

    @property
    def perms_map(self):
        methods = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')
        perms = dict()
        for method in methods:
            perms.update(**{method: self.__getattribute__(method.lower())})
        return perms

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return super().has_permission(request, view)

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_underline_name': camel2underline(model_cls.__name__, smart=True)
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class BaseModelPermissionsOrAnonReadOnly(BaseModelPermissions):
    authenticated_users_only = False


class StrictModelPermissions(BaseModelPermissions):
    get = ['%(app_label)s.view_%(model_underline_name)s']
    head = ['%(app_label)s.view_%(model_underline_name)s']


def login_required(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if getattr(self, 'permission_classes', []):
            if not bool(request.user and request.user.is_authenticated):
                raise exceptions.NotAuthenticated()
        return func(self, request, *args, **kwargs)

    return wrapper
