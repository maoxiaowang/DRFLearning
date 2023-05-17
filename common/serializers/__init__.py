from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        declare_fields = set(dict(**self._declared_fields))
        existing_fields = set(self.fields)
        allowed_fields = set(fields) if fields else set()
        extra_fields = set(self.Meta.extra_fields)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        self.Meta.fields = list((existing_fields | declare_fields | extra_fields) - allowed_fields)
        self.Meta.exclude = None


class PureSerializerMixin:
    def create(self, validated_data):
        raise PermissionDenied

    def update(self, instance, validated_data):
        raise PermissionDenied


class Serializer(PureSerializerMixin, serializers.Serializer):
    pass
