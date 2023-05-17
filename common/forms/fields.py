import json

from django import forms
from django.core.exceptions import ValidationError

from common.logging import loggers
from common.validators import ListFieldValidator, DictFieldValidator

logger = loggers.service


class JsonField(forms.CharField):
    default_error_messages = {
        'invalid_json': 'Value %(value)s is not a jsonable string.'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'],
                code='required',
                params={'value': value}
            )

        if value in self.empty_values:  # empty_values和blank有关
            return value
        # if isinstance(value, (dict, list)):
        #     return value
        else:
            if value is None:
                return
            try:
                return json.loads(value)
            except json.decoder.JSONDecodeError as e:
                raise ValidationError(
                    self.error_messages['invalid_json'],
                    code='invalid_json',
                    params={'value': value}
                )


class ListField(JsonField):
    description = 'list'

    def get_internal_type(self):
        return "ListField"

    default_error_messages = {
        'invalid_json': "Value '%(value)s' is not a list-like string or null."
    }
    default_validators = [ListFieldValidator()]


class DictField(JsonField):
    description = 'dict'

    def get_internal_type(self):
        return "DictField"

    default_error_messages = {
        'invalid_json': 'Value %(value)s is not a dict-like string or null.'
    }
    default_validators = [DictFieldValidator()]
