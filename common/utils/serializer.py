import typing

from rest_framework import serializers


def model_serializer_factory(model_class, fields: typing.Iterable = None, exclude_fields=None,
                             bases: tuple = None, class_name=None, enable_relation=False):
    """
    简单的模型序列化器，建议只包含基础字段
    enable_relation默认不启用，启用后序列化第二层关系字段
    """
    meta_class = type('Meta', (), {'model': model_class, 'fields': fields or '__all__'})
    meta = getattr(model_class, '_meta')
    concrete_fields = meta.concrete_fields

    if fields:
        concrete_fields = [field for field in concrete_fields if field.name in fields]
    if exclude_fields:
        concrete_fields = [field for field in concrete_fields if field.name not in exclude_fields]

    attrs = dict()

    if enable_relation:
        # 外键和一对一
        related_fields = [field for field in concrete_fields if field.many_to_one or field.one_to_one]
        for field in related_fields:
            attrs[field.name] = model_serializer_factory(field.related_model).__call__()

    attrs['Meta'] = meta_class

    if not bases:
        bases = (serializers.ModelSerializer,)
    assert serializers.ModelSerializer in bases
    if not class_name:
        class_name = f'{meta.object_name}Serializer'

    serializer_class = type(class_name, bases, attrs)
    return serializer_class


def serializer_factory(bases: tuple = None, fields: dict = None, class_name='FactorySerializer'):
    if not bases:
        bases = (serializers.Serializer,)
    if not fields:
        fields = {}

    for name, field in fields:
        assert isinstance(field, serializers.Field)

    serializer_class = type(class_name, bases, fields)
    return serializer_class
