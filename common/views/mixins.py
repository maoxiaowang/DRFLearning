from django.db import IntegrityError
from rest_framework import mixins as _mixins, serializers
from rest_framework import status
from rest_framework.generics import get_object_or_404

from common.views.response import Response


class CreateModelMixin(_mixins.CreateModelMixin):
    create_response = Response
    create_serializer_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.create_serializer_class or self.serializer_class
        return super().get_serializer_class()

    @staticmethod
    def get_response_data(serializer):
        return serializer.data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if hasattr(serializer, 'Meta'):
            serializer.Meta.model.request_user = request.user
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = self.get_response_data(serializer)
        return self.create_response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class ListModelMixin:
    """
    List a queryset.
    """
    list_response = Response

    def _handle_serializer_data(self, serializer_data):
        return serializer_data

    def list(self, request, *args, **kwargs):
        # 优先拿queryset属性（有permission校验会先获取）
        queryset = self.queryset if self.queryset is not None else self.get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self._handle_serializer_data(serializer.data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = self._handle_serializer_data(serializer.data)

        return self.list_response(data)


class RetrieveModelMixin:
    """
    Retrieve a model instance.
    """
    retrieve_response = Response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = self._handle_serializer_data(serializer.data, instance)
        return self.retrieve_response(data)

    def _handle_serializer_data(self, serializer_data, instance):
        return serializer_data


class UpdateModelMixin(_mixins.UpdateModelMixin):
    update_response = Response
    update_serializer_class = None

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'POST', 'PATCH'):  # 支持post
            return self.update_serializer_class or self.serializer_class
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        instance.request_user = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return self.update_response(serializer.data)


class DestroyModelMixin(_mixins.DestroyModelMixin):
    """
    Destroy a model instance.
    """
    destroy_response = Response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.request_user = request.user
        self.perform_destroy(instance)
        return self.destroy_response(status=status.HTTP_200_OK)


class BaseSetMixin:
    serializer_class = None
    related_name = None  # model related name (required)
    request_field_name = None  # request field name (optional, default as same as related_name)
    model = None
    pk_url_kwarg = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['GET', 'HEAD', 'OPTION']:
            assert self.serializer_class is not None, (
                    "'%s' should either include a `serializer_class` attribute, "
                    "or override the `get_serializer_class()` method."
                    % self.__class__.__name__
            )
            serializer_cls = self.serializer_class
        else:
            serializer_cls = type(
                f'{self.__class__.__name__}Serializer',
                (serializers.Serializer,),
                {self.request_field_name: serializers.ListField()}
            )
        return serializer_cls


class M2MListModelMixin(BaseSetMixin, ListModelMixin):

    def dispatch(self, request, *args, **kwargs):
        assert self.model, 'The attribute model is required.'
        if not self.request_field_name:
            self.request_field_name = self.related_name
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(self.model, pk=pk)

    def get_queryset(self):
        assert self.related_name, 'The attribute related_name is required.'
        instance = self.get_object()
        return getattr(instance, self.related_name).all()


class M2MAddModelMixin(BaseSetMixin):
    add_response = Response

    def dispatch(self, request, *args, **kwargs):
        if not self.request_field_name:
            self.request_field_name = self.related_name
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.model.objects.get(pk=pk)

    def add(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        self.perform_add(serializer, instance)
        return self.add_response(status=status.HTTP_201_CREATED)

    def perform_add(self, serializer, instance):
        assert self.related_name, 'The attribute related_name is required.'
        data_set = serializer.data[self.request_field_name]
        for pk in data_set:
            try:
                getattr(instance, self.related_name).add(pk)
            except IntegrityError:
                # 如果使用了through创建m2m表，这里找不到外键可能会抛异常
                continue


class M2MRemoveModelMixin(BaseSetMixin):
    remove_response = Response

    def dispatch(self, request, *args, **kwargs):
        if not self.request_field_name:
            self.request_field_name = self.related_name
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.model.objects.get(pk=pk)

    def remove(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        self.perform_remove(serializer, instance)
        return self.remove_response()

    def perform_remove(self, serializer, instance):
        assert self.related_name, 'The attribute related_name is required.'
        data_set = serializer.data[self.request_field_name]
        for pk in data_set:
            getattr(instance, self.related_name).remove(pk)


class SetListModelMixin(ListModelMixin):
    lookup_url_kwarg = 'pk'
    model = None

    def get_object(self):
        pk = self.kwargs.get(self.lookup_url_kwarg)
        return self.model.objects.get(pk=pk)
