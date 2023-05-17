from django.core.cache import cache
from django.db import models

__all__ = [
    "CustomManager",
    'CacheManager',
    'ResourceManager'
]


class CustomManager(models.Manager):
    """
    Supported method:
    create, update, get_or_create, update_or_create
    """

    def handle_kwargs(self, **kwargs):
        fields = self.model._meta.concrete_fields
        fields_attname = [field.attname for field in fields]
        [kwargs.pop(arg) for arg in list(kwargs.keys()) if
         arg not in fields_attname]
        return kwargs


INSTANCE = 'I'
QUERYSET = 'Q'


class CacheManager(models.Manager):
    """
    暂不支持跨表缓存
    """

    cache_seconds = 5 * 60  # 默认缓存过期时间

    def __init__(self, cache_seconds=None, **kwargs):
        super().__init__(**kwargs)
        self.cache_seconds = cache_seconds or self.cache_seconds

    def _makeup_key(self, data_type, *args, **kwargs):
        """
        args 暂时不用
        """
        assert data_type in (INSTANCE, QUERYSET)
        sorted_kwargs = sorted(kwargs.items(), key=lambda i: i[0])
        post = ':'.join(map(lambda x: x[0] + '.' + str(x[1]), sorted_kwargs))
        model_label = self.model._meta.label
        key = '%s:%s:%s' % (data_type, model_label, post)
        # print('key: %s' % key)
        return key

    def set_expire(self, seconds):
        self.cache_seconds = seconds

    def _update_cache(self, key, obj):
        cache.set(key, obj, self.cache_seconds)

    def get(self, *args, use_cache=True, update_cache=True, **kwargs):
        """
        一般来说get的kwargs使用primary key
        use_cache：使用缓存，优先从缓存中读取
        update_cache：任何情况下都更新缓存
        """
        key = self._makeup_key(INSTANCE, *args, **kwargs)
        if use_cache:
            _cache = cache.get(key)
            if _cache:
                return _cache
            try:
                instance = super().get(*args, **kwargs)
            except self.model.DoesNotExist:
                cache.delete(key)
                raise
            if use_cache:
                self._update_cache(key, instance)
            return instance

        instance = super().get(*args, **kwargs)
        if update_cache:
            self._update_cache(key, instance)
        return instance

    def filter(self, *args, use_cache=False, update_cache=True, **kwargs):
        key = self._makeup_key(QUERYSET, *args, **kwargs)
        if use_cache:
            _cache = cache.get(key)
            if _cache:
                return _cache
            queryset = super().filter(*args, **kwargs)
            if update_cache:
                self._update_cache(key, queryset)
            return queryset
        queryset = super().filter(*args, **kwargs)
        if update_cache:
            self._update_cache(key, queryset)
        return queryset

    def all(self, use_cache=False, update_cache=True):
        key = self._makeup_key(QUERYSET)
        if use_cache:
            _cache = cache.get(key)
            if _cache:
                return _cache
            queryset = super().all()
            if update_cache:
                self._update_cache(key, queryset)
            return queryset
        queryset = super().all()
        if update_cache:
            self._update_cache(key, queryset)
        return queryset

    def delete(self):
        return super().delete()


class ResourceManager(models.Manager):
    """
    Supported method:
    create, update, get_or_create, update_or_create
    """

    def _extract_model_params(self, **kwargs):
        fields = self.model._meta.concrete_fields
        field_attnames = [field.attname for field in fields if field.many_to_one or field.one_to_one]
        field_names = [field.name for field in fields]
        field_names += field_attnames
        [kwargs.pop(arg) for arg in list(kwargs.keys()) if
         arg not in field_names]
        return kwargs

    def get_or_none(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            return

    def create(self, **kwargs):
        """
        Create a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        kwargs = self._extract_model_params(**kwargs)
        obj = super().create(**kwargs)
        return obj

    def get_or_create(self, defaults=None, **kwargs):
        defaults = defaults or {}
        defaults = self._extract_model_params(**defaults)
        return super().get_or_create(defaults=defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        defaults = defaults or {}
        defaults = self._extract_model_params(**defaults)
        return super().update_or_create(defaults=defaults, **kwargs)
