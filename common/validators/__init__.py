import json
import re

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from common.utils.regex import MOBILE_REGEX, SMS_CODE_REGEX, GLOBAL_MOBILE_REGEX


@deconstructible
class ListFieldValidator(validators.RegexValidator):
    regex = r'^(\[.*?\]|null)$'
    message = 'List field only accepts list-like or null string'
    flags = re.UNICODE

    def __call__(self, value):
        if isinstance(value, str):
            super().__call__(value)
        elif isinstance(value, list):
            pass
        else:
            raise ValidationError(self.message, code=self.code, params={'value': value})


@deconstructible
class DictFieldValidator(validators.RegexValidator):
    regex = r'^(\{.*?\}|null)$'
    message = _(
        'Enter a valid username. This value may contain only English letters, '
        'numbers, and @/./+/-/_ characters.'
    )
    flags = re.UNICODE


class MobilePhoneValidator(validators.RegexValidator):
    regex = MOBILE_REGEX
    message = _(
        'Enter a valid mobile phone number.'
    )


class GlobalMobilePhoneValidator(MobilePhoneValidator):
    regex = GLOBAL_MOBILE_REGEX


class SMSCodeValidator(validators.RegexValidator):
    regex = SMS_CODE_REGEX
    message = _(
        'Enter a valid sms code.'
    )


class StringJSONValidator:
    message = 'Enter a valid JSON string, which contains only string elements.'
    code = 'invalid_format'

    def __call__(self, value):
        error = ValidationError(self.message, code=self.code)
        try:
            value = json.loads(value)
        except json.decoder.JSONDecodeError:
            raise error
        if not isinstance(value, list):
            raise error
        for item in value:
            if not isinstance(item, str):
                raise error
